from abc import ABC, abstractmethod
from src.DataAcquisition.GitHubAPIService.RESTService.GitHubRESTWrapper import GitHubRESTWrapper
from src.Utility.Utility import null_if_none, dict_search
from github import Issue


class RESTNode(ABC):
    def __init__(self, github_rest_api: GitHubRESTWrapper):
        self._github_rest_api = github_rest_api

    @abstractmethod
    def get_data(self) -> []:
        pass

    def get_github_rest_api(self) -> GitHubRESTWrapper:
        return self._github_rest_api


class RESTRootNode(ABC):
    def __init__(self, github_rest_api: GitHubRESTWrapper, node_number: int):
        self._node_number = node_number
        self._github_rest_api = github_rest_api
        self._children: [RESTNode] = []

    @abstractmethod
    def get_data(self) -> dict:
        pass

    def get_github_rest_api(self) -> GitHubRESTWrapper:
        return self._github_rest_api

    def get_node_number(self):
        return self._node_number


# ISSUE

class IssueLabels(RESTNode):
    """
    Collects issue labels with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, issue: Issue):
        super().__init__(github_rest_api)
        self.issue = issue

    def get_data(self) -> []:
        issue_labels = dict_search(self.issue._rawData, ["labels"], [])
        return [
            {
                "id": dict_search(label, ["node_id"], ""),
                "name": dict_search(label, ["name"], "")
            } for label in issue_labels
        ]


class IssueTimeline(RESTNode):
    """
    Collects issue timeline with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, issue: Issue):
        super().__init__(github_rest_api)
        self.issue = issue

    def get_data(self) -> []:
        timeline = []
        for event in self.get_github_rest_api().get_issue_events(self.issue):
            event_data = {
                "__typename": dict_search(event._rawData, ["event"], ""),
                "createdAt": dict_search(event._rawData, ["created_at"], "")
            }
            if event_data.get("__typename") == "closed":
                event_data.update({
                    "__typename": "ClosedEvent",
                    "id": dict_search(event._rawData, ["node_id"], ""),
                    "createdAt": dict_search(event._rawData, ["created_at"], ""),
                    "actor": None if dict_search(event._rawData, ["actor"], None) is None else {
                        "id": dict_search(event._rawData, ["actor", "node_id"], ""),
                        "name": "",
                        "login": dict_search(event._rawData, ["actor", "login"], ""),
                        "email": ""
                    }
                })
            if event_data.get("__typename") == "converted_to_discussion":
                event_data.update({
                    "__typename": "ConvertedToDiscussionEvent",
                    "id": dict_search(event._rawData, ["node_id"], "")
                })
            timeline.append(event_data)
        return timeline


class IssueComments(RESTNode):
    """
    Collects issue comments with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, issue: Issue):
        super().__init__(github_rest_api)
        self.issue = issue

    def get_data(self) -> []:
        return [
            {
                "id": dict_search(comment._rawData, ["node_id"], ""),
                "createdAt": dict_search(comment._rawData, ["created_at"], ""),
                "body": dict_search(comment._rawData, ["body"], ""),
                "author": None if comment.user is None else {
                    "id": dict_search(comment._rawData, ["user", "node_id"], ""),
                    "name": "",
                    "email": "",
                    "login": dict_search(comment._rawData, ["user", "login"], "")
                }
            } for comment in self.get_github_rest_api().get_issue_comments(self.issue)
        ]


class IssueAssignees(RESTNode):
    """
    Collects assignees timeline with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, issue: Issue):
        super().__init__(github_rest_api)
        self.issue = issue

    def get_data(self) -> []:
        issue_assignees = dict_search(self.issue._rawData, ["assignees"], [])
        return [
            {
                "id": dict_search(assignee, ["node_id"], ""),
                "login": dict_search(assignee, ["login"], ""),
                "name": "",
                "email": ""
            } for assignee in issue_assignees if dict_search(assignee, ["node_id"], "") != ""
        ]


class IssueRoot(RESTRootNode):
    """
    Collects issue data with the REST API
    """

    def get_data(self) -> dict:
        issue = self.get_github_rest_api().get_issue(self.get_node_number())
        return {
            "nodes": [
                {
                    "id": dict_search(issue._rawData, ["node_id"], ""),
                    "number": dict_search(issue._rawData, ["number"], -1),
                    "title": dict_search(issue._rawData, ["title"], ""),
                    "body": dict_search(issue._rawData, ["body"], ""),
                    "state": dict_search(issue._rawData, ["state"], "").upper(),
                    "createdAt": dict_search(issue._rawData, ["created_at"], ""),
                    "milestone": None if issue.milestone is None else {
                        "id": dict_search(issue._rawData, ["milestone", "node_id"], ""),
                        "number": dict_search(issue._rawData, ["milestone", "number"], -1),
                        "title": dict_search(issue._rawData, ["milestone", "title"], ""),
                        "description": dict_search(issue._rawData, ["milestone", "description"], ""),
                        "dueOn": dict_search(issue._rawData, ["milestone", "due_on"], ""),
                        "createdAt": dict_search(issue._rawData, ["milestone", "created_at"], ""),
                        "closedAt": dict_search(issue._rawData, ["milestone", "closed_at"], ""),
                        "progressPercentage": 100 * (issue.milestone.closed_issues / (
                                issue.milestone.open_issues + issue.milestone.closed_issues)),
                        "state": dict_search(issue._rawData, ["milestone", "state"], "").upper(),
                        "creator": None if issue.milestone.creator is None else {
                            "id": dict_search(issue._rawData, ["milestone", "creator", "node_id"], ""),
                            "login": dict_search(issue._rawData, ["milestone", "creator", "login"], ""),
                            "email": "",
                            "name": ""
                        }
                    },
                    "timelineItems": {
                        "nodes": IssueTimeline(self.get_github_rest_api(), issue).get_data()
                    },
                    "author": None if issue.user is None else {
                        "id": null_if_none(issue.user.node_id),
                        "name": "",
                        "login": null_if_none(issue.user.login),
                        "email": ""
                    },
                    "assignees": {
                        "nodes": IssueAssignees(self.get_github_rest_api(), issue).get_data()
                    },
                    "labels": {
                        "nodes": IssueLabels(self.get_github_rest_api(), issue).get_data()
                    },
                    "comments": {
                        "nodes": IssueComments(self.get_github_rest_api(), issue).get_data()
                    }
                }
            ]
        }
