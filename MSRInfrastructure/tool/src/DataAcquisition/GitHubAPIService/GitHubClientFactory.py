from src.DataAcquisition.GitHubAPIService.TokenManager import TokenManager
from src.DataAcquisition.GitHubAPIService.RESTService.GitHubRESTWrapper import GitHubRESTWrapper
from src.DataAcquisition.GitHubAPIService.GraphQLService.GitHubGraphQLWrapper import GitHubGraphQLWrapper
from src.DataAcquisition.GitHubAPIService.GitHubAPIType import GITHUB_API_TYPE
from typing import Optional

class GitHubClientFactory:
    """
    Interface to orchestrate the creation of GitHub REST and GraphQL wrapper classes. Ensures that clients
    are properly destroyed after use next to proper initialization in advance to usage.
    """

    def __init__(self, repo_owner: str, repo_name: str, token_manager: TokenManager):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        # Indicates the last accessed API
        self.last_accessed_api: Optional[GITHUB_API_TYPE] = None
        # Indicates the value of the last accessed API
        self.api_value = None
        self.REST_API_CLIENT = GitHubRESTWrapper(token_manager, self.repo_owner, self.repo_name)
        self.GRAPHQL_API_CLIENT = GitHubGraphQLWrapper(token_manager, self.repo_owner, self.repo_name)

    def destroy_client(self):
        if self.api_value is not None:
            self.api_value.destroy_client()

    def get_rest_api(self) -> GitHubRESTWrapper:
        if self.last_accessed_api != GITHUB_API_TYPE.REST_API:
            # Destroy the old client
            if self.api_value is not None:
                self.api_value.destroy_client()
            # Start the client
            self.api_value = self.REST_API_CLIENT
            self.api_value.start_client()
        # Update the last accessed value
        self.last_accessed_api = GITHUB_API_TYPE.REST_API
        return self.api_value

    def get_graphql_api(self) -> GitHubGraphQLWrapper:
        if self.last_accessed_api != GITHUB_API_TYPE.GRAPH_QL_API:
            # Destroy the old client
            if self.api_value is not None:
                self.api_value.destroy_client()
            # Start the client
            self.api_value = self.GRAPHQL_API_CLIENT
            self.api_value.start_client()
        # Update the last accessed value
        self.last_accessed_api = GITHUB_API_TYPE.GRAPH_QL_API
        return self.api_value
