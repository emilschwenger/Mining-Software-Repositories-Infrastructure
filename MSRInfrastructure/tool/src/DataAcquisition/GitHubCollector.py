from enum import Enum

from src.DataAcquisition.GitHubAPIService.GraphQLService import GitHubGraphQLWrapper
from src.DataAcquisition.GitHubAPIService.RESTService.GitHubRESTWrapper import GitHubRESTWrapper

from src.DataAcquisition.GitHubAPIService.GraphQLService.GraphQLQueryTree import GraphQLRootNode
from src.DataAcquisition.GitHubAPIService.GraphQLService.ProjectQuery import ProjectRoot
from src.DataAcquisition.GitHubAPIService.GraphQLService.DiscussionQuery import DiscussionRoot

from src.DataAcquisition.GitHubAPIService.RESTService.PullRequestQuery import PullRequestRoot
from src.DataAcquisition.GitHubAPIService.RESTService.IssueQuery import IssueRoot
from src.DataAcquisition.GitHubAPIService.RESTService.CommitQuery import CommitsRoot
from src.DataAcquisition.GitHubAPIService.RESTService.SBOMQuery import SBOMRoot
from src.DataAcquisition.GitHubAPIService.RESTService.WorkflowQuery import WorkflowRoot
from src.DataAcquisition.GitHubAPIService.RESTService.PullRequestFileActionsQuery import PullRequestFileActionsRoot


class DATA_TREE(Enum):
    """
    DATA_TREE contains a list of objects that the GraphQL collector get() methods can return automatically in
    an iterative fashion
    """
    ISSUE = "issues"
    PULL_REQUEST = "pullRequests"
    WATCHER = "watchers"
    STARGAZER = "stargazers"
    DISCUSSION = "discussions"
    RELEASE = "releases"
    LABEL = "labels"


class GraphQLCollector:
    """
    This class provides prebuilt functionality to retrieve data from the GitHub GraphQL API.
    NOTE: The GraphQLCollector and RESTCollector deliver Issues and PullRequests query results in the exact same format.
    """

    def __init__(self, graphql_client: GitHubGraphQLWrapper):
        self.graphql_client = graphql_client

    def get(self, secondary_root_nodes: [DATA_TREE], exceptions: [DATA_TREE]):
        """
        Generator to collect different types of nodes with the GraphQL API. Node cursors automatically advance in
        the first layer by parsing the query result before returning it.
        VALID NODES: ISSUE, PULL_REQUEST, STARGAZER, WATCHER, DISCUSSION, RELEASE, LABEL
        :param exceptions: List of node names that will not prevent the query from terminating. After collecting
        all other nodes the query will stop.
        :param secondary_root_nodes: List of node names that the query requests. (Exceptions must be contained)
        :return: (query_result: dict, partially_collected_nodes: dict)
        """
        # Construct the root node
        root_node = GraphQLRootNode(
            [secondary_root_node.value for secondary_root_node in secondary_root_nodes],
            [exception.value for exception in exceptions]
        )
        # Loop over query results
        while True:
            query, is_query_finished = root_node.get_query_content()
            # If collection is complete -> Terminate
            if is_query_finished:
                return
            # Execute the query
            query_result = self.graphql_client.execute(query)
            # Parse the result into the query builder to update cursors
            partially_collected_nodes = root_node.parse_result(query_result)
            # Return the query results and the nodes that are only partially collected
            yield query_result, partially_collected_nodes

    def get_discussion(self, number: int):
        """
        Generator to get all discussion comments for a specific discussion number.
        :param number: int
        :return: query_result: dict
        """
        # Construct the discussion root node
        root_node = DiscussionRoot(number)
        # Loop over query results
        while True:
            query, is_query_finished = root_node.get_query_content()
            # If collection is complete -> Terminate
            if is_query_finished:
                return
            # Execute the query
            query_result = self.graphql_client.execute(query)
            # Parse the result into the query builder to update cursor
            root_node.parse_result(query_result)
            yield query_result

    def get_remaining_token(self):
        """
        Get the amount of remaining token points for the currently used token. (GraphQL)
        :return: int
        """
        return self.graphql_client.get_remaining_token()

    def get_project(self):
        """
        Retrieves relevant project metadata.
        :return: query_result: dict
        """
        project_query = ProjectRoot().get_query_content()
        return self.graphql_client.execute(project_query)


class RESTCollector:
    """
    This class provides prebuilt functionality to retrieve data from the GitHub REST API.
    NOTE: The GraphQLCollector and RESTCollector deliver Issues and PullRequests query results in the exact same format.
    """

    def __init__(self, rest_client: GitHubRESTWrapper):
        self.rest_client = rest_client

    def get_issues(self, node_numbers: [int]):
        """
        Generator to collect multiple issues with the REST API
        :param node_numbers: a list of node numbers
        :return: Each iteration a dictionary of the issue results
        """
        for node_number in node_numbers:
            root_node = IssueRoot(self.rest_client, node_number)
            yield root_node.get_data()

    def get_pull_requests(self, node_numbers: [int]):
        """
        Generator to collect multiple pull requests with the REST API
        :param node_numbers: a list of node numbers
        :return: Each iteration a dictionary of the pull request results
        """
        for node_number in node_numbers:
            root_node = PullRequestRoot(self.rest_client, node_number)
            yield root_node.get_data()

    def get_workflows(self):
        """
        Generator to collect all workflows and workflow runs with the REST API
        :return: Each iteration a dictionary
        """
        for workflow in WorkflowRoot(self.rest_client).get_data():
            yield workflow

    def get_sbom(self) -> []:
        """
        Get all dependencies of a repository.
        :return: dependencies as list of dictionaries
        """
        return SBOMRoot(self.rest_client).get_data()

    def get_remaining_token(self):
        """
        Get the amount of remaining token points for the currently used token. (REST API)
        :return: int
        """
        return self.rest_client.get_remaining_token()

    def get_commits(self):
        """
        Generator to get commit meta information. (author/committer/commit comments)
        """
        for commit in CommitsRoot(self.rest_client).get_data():
            yield commit

    def get_repository_pull_request_file_actions(self):
        """
        Generator for all file actions of GitHub pull requests
        :return: Each iteration a single file actions as a dictionary
        """
        for pull_request_file_action in PullRequestFileActionsRoot(self.rest_client).get_data():
            yield pull_request_file_action
