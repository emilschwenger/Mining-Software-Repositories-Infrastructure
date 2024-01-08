from src.DataAcquisition.GitHubAPIService.RESTService.GitHubRESTWrapper import GitHubRESTWrapper
from src.Utility.Utility import dict_search


class WorkflowRoot:
    """
    Collects workflows with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper):
        self._github_rest_api = github_rest_api

    def get_data(self):
        """
        Generator to retrieve all workflows and workflow runs.
        :return: dict
        """
        for workflow in self._github_rest_api.get_workflows():
            yield {
                "id": dict_search(workflow._rawData, ["node_id"], ""),
                "title": dict_search(workflow._rawData, ["name"], ""),
                "configPath": dict_search(workflow._rawData, ["path"], ""),
                "createdAt": dict_search(workflow._rawData, ["created_at"], ""),
                "state": dict_search(workflow._rawData, ["state"], ""),
                "workflowRuns": [
                    {
                        "id": dict_search(workflow_run._rawData, ["node_id"], ""),
                        "status": dict_search(workflow_run._rawData, ["status"], ""),
                        "conclusion": dict_search(workflow_run._rawData, ["conclusion"], ""),
                        "createdAt": dict_search(workflow_run._rawData, ["created_at"], ""),
                        "startedAt": dict_search(workflow_run._rawData, ["run_started_at"], ""),
                        "attempts": dict_search(workflow_run._rawData, ["run_attempt"], -1),
                        "headCommit": dict_search(workflow_run._rawData, ["head_sha"], ""),
                        "actor": None if dict_search(workflow_run._rawData, ["actor"], None) is None else {
                            "id": dict_search(workflow_run._rawData, ["actor", "node_id"], ""),
                            "login": dict_search(workflow_run._rawData, ["actor", "login"], ""),
                            "email": "",
                            "name": ""
                        },
                        "triggeringActor": None if dict_search(workflow_run._rawData, ["triggering_actor"], None) is None else{
                            "id": dict_search(workflow_run._rawData, ["triggering_actor", "node_id"], ""),
                            "login": dict_search(workflow_run._rawData, ["triggering_actor", "login"], ""),
                            "email": "",
                            "name": ""
                        },
                    } for workflow_run in self._github_rest_api.get_workflow_runs(workflow)
                ]
            }
