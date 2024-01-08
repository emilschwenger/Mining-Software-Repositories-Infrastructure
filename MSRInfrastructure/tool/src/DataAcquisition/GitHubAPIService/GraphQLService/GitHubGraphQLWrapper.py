import os
import time

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from src.DataAcquisition.GitHubAPIService.TokenManager import TokenManager
from datetime import datetime
from typing import Union
from src.DataAcquisition.GitHubAPIService.GitHubAPIType import GITHUB_API_TYPE
from src.Utility.Logger import MSRLogger

# Inspired by gql 3 documentation https://gql.readthedocs.io/
class GitHubGraphQLWrapper():
    """
    A wrapper to query the GitHub GraphQL API.
    """

    def __init__(self, token_manager: TokenManager, repo_owner: str, repo_name: str):
        self.token_manager: TokenManager = token_manager
        self.logger = MSRLogger.get_logger(self.__class__.__name__)
        self.repo_owner: str = repo_owner
        self.repo_name: str = repo_name
        self.repo = self.repo_owner + "/" + self.repo_name
        self.token: str = ""
        self.time_format: str = "%Y-%m-%dT%H:%M:%SZ"
        self.reuse_time: datetime = datetime.min
        self.rate_limit_exceeded: bool = False
        self.running: bool = False
        self.github: Union[Client, None] = None
        self._remaining_token = 5000
        self._MIN_TOKEN_COUNT = 50
        self._WAITING_TIME = 0.5

    def start_client(self):
        """
        Starts the client and handles all administrative tasks.
        """
        self.reuse_time = datetime.min
        self.rate_limit_exceeded = False
        self.running = True
        self.token = ""
        self.github = self._create_client()

    def _set_reuse_time(self, reuse_time: str):
        """
        Sets the token reuse_time
        :param reuse_time: Format 'YYYY-MM-DDTHH:MM:SSZ'
        """
        self.reuse_time = datetime.strptime(reuse_time, self.time_format)

    def _create_client(self) -> Client:
        """
        Creates a client and loads the schema to validate requests.
        :return: client: Client
        """
        self.token = self.token_manager.get_token(GITHUB_API_TYPE.GRAPH_QL_API)
        transport = RequestsHTTPTransport(
            url="https://api.github.com/graphql",
            retries=5,
            headers={
                "Authorization": "bearer " + self.token
            }
        )
        # Read GitHub GraphQL Schema for query validation
        with open(os.path.dirname(__file__) + "/GitHubGraphQLSchema/github-schema.graphql") as f:
            schema = f.read()
        return Client(transport=transport, schema=schema)

    def destroy_client(self):
        """
        Destroys the client.
        """
        if not self.running:
            self.logger.exception(f"{self.repo} Destroying client failed -> client is not running")
        else:
            self.running = False
            self.github = None
            # Return token
            if self.rate_limit_exceeded:
                self.token_manager.return_token(self.token, GITHUB_API_TYPE.GRAPH_QL_API, self.reuse_time)
                self.logger.info(f"{self.repo} Client with token: {self.token} successfully destroyed | reuse_time {self.reuse_time}")
            else:
                self.token_manager.return_token(self.token, GITHUB_API_TYPE.GRAPH_QL_API)
                self.logger.info(f"{self.repo} Client with token: {self.token} successfully destroyed | immediate reuse")
            self.rate_limit_exceeded = False
            self.reuse_time = datetime.min

    def _process_rate_limit(self, rate_limit: dict):
        """
        Processes query rate limits.
        :param rate_limit: {"rateLimit": { "resetAt": "Y-M-DTH:M:SZ", "remaining": int} }
        """
        # Set the remaining token amount
        self._remaining_token = rate_limit.get("remaining", 0)

        # Threshold of _MIN_TOKEN_COUNT before marking token as rate_limit_exceeded
        if self._remaining_token <= self._MIN_TOKEN_COUNT:
            self.logger.info(f"{self.repo} Token count below {self._MIN_TOKEN_COUNT} for token: {self.token}")
            self.rate_limit_exceeded = True
            self._set_reuse_time(rate_limit.get("resetAt"))

        # Reset client, create new client, and reset reuse time in case of rate limit exceeded
        if self.rate_limit_exceeded:
            self.logger.info(f"{self.repo} Rate limit exceeded -> acquiring new client")
            self.destroy_client()
            self.start_client()

    def execute(self, query: str):
        """
        Execute a graphql query.
        :param query: query
        :return:
        """
        if not self.running:
            self.logger.exception(f"{self.repo} Can not execute request -> client is not running")
        query = '''
        !
            repository(owner: "{repo_owner}", name: "{repo_name}") !
                {query}
            ?
            rateLimit !
                remaining
                cost
                resetAt
            ?
        ?
        '''.format(repo_owner=self.repo_owner, repo_name=self.repo_name, query=query).replace("!", "{").replace("?", "}")
        gql_code = gql(query)
        try:
            query_result = self.github.execute(gql_code)
            time.sleep(self._WAITING_TIME)
        except Exception as e:
            # TODO: Implement more robust query error handling
            self.destroy_client()
            self.start_client()
            query_result = self.execute_raw(query)
            self.logger.info(f"{self.repo} Exception occurred during graphql query execution")
        self._process_rate_limit(query_result.get("rateLimit", {}))
        return query_result

    def execute_raw(self, query: str):
        """
        Execute a graphql query without preset repository template.
        NOTE: the query must return rateLimit {remaining, resetAt}
        :param query: query
        :return:
        """
        if not self.running:
            self.logger.exception(f"{self.repo} Cannot execute request -> client is not running")
        gql_code = gql(query)
        try:
            query_result = self.github.execute(gql_code)
            time.sleep(self._WAITING_TIME)
        except Exception as e:
            # TODO: Implement more robust query error handling
            self.destroy_client()
            self.start_client()
            query_result = self.execute_raw(query)
            self.logger.info(f"{self.repo} Exception occurred during graphql query execution")
        self._process_rate_limit(query_result.get("rateLimit", {}))
        return query_result

    def get_remaining_token(self):
        return self._remaining_token
