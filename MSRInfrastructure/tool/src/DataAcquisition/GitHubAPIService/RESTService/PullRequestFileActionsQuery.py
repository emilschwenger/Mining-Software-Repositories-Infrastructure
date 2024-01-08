from src.DataAcquisition.GitHubAPIService.RESTService.GitHubRESTWrapper import GitHubRESTWrapper
from src.Utility.Utility import dict_search


class PullRequestFileActionsRoot:
    """
    Collects pull request file actions with the REST API (EXPENSIVE)
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper):
        self._github_rest_api = github_rest_api

    def get_data(self):
        """
        Generator to retrieve all pull request file actions
        :return: dict
        """
        for pull_request in self._github_rest_api.get_pull_requests():
            for file_action in self._github_rest_api.get_repository_pull_request_file_actions(pull_request):
                yield {
                    "pullRequestId": dict_search(pull_request._rawData, ["node_id"], ""),
                    "sha": dict_search(file_action._rawData, ["sha"], ""),
                    "path": dict_search(file_action._rawData, ["filename"], ""),
                    "changeType": dict_search(file_action._rawData, ["status"], "").upper(),
                    "additions": dict_search(file_action._rawData, ["additions"], -1),
                    "deletions": dict_search(file_action._rawData, ["deletions"], -1),
                    "changes": dict_search(file_action._rawData, ["changes"], -1),
                    "patch": dict_search(file_action._rawData, ["patch"], "")
                }
