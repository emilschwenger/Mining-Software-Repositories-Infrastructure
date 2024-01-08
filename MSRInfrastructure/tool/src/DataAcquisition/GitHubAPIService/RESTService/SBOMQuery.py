from src.DataAcquisition.GitHubAPIService.RESTService.GitHubRESTWrapper import GitHubRESTWrapper
from src.Utility.Utility import dict_search


class SBOMRoot:
    """
    Collects SBOM with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper):
        self._github_rest_api = github_rest_api

    def get_data(self) -> []:
        """
        Get the dependencies of repository.
        :return: dependencies as list
        """
        sbom = self._github_rest_api.send_custom_request(endpoint="/dependency-graph/sbom")
        if sbom is None:
            return []
        else:
            return dict_search(sbom, ["sbom", "packages"], [])
