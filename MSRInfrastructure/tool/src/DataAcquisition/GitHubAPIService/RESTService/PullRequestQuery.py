from abc import ABC, abstractmethod
from src.DataAcquisition.GitHubAPIService.RESTService.GitHubRESTWrapper import GitHubRESTWrapper
from src.Utility.Utility import dict_search
from github import PullRequest


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


# PULL REQUEST

class PullRequestTimeline(RESTNode):
    """
    Collects pull request timeline with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, pull_request: PullRequest):
        super().__init__(github_rest_api)
        self.pull_request = pull_request

    def get_data(self) -> []:
        timeline = []
        for event in self.get_github_rest_api().get_pull_request_timeline(self.pull_request):
            event_data = {}
            event_name = dict_search(event._rawData, ["event"], "")
            if event_name is None:
                continue
            if event_name == "merged":
                event_data.update({
                    "__typename": "MergedEvent",
                    "id": dict_search(event._rawData, ["node_id"], ""),
                    "createdAt": dict_search(event._rawData, ["created_at"], ""),
                    "actor": None if event.actor is None else {
                        "id": dict_search(event._rawData, ["actor", "node_id"], ""),
                        "name": "",
                        "login": dict_search(event._rawData, ["actor", "login"], ""),
                        "email": ""
                    },
                    "commit": {
                        "oid": dict_search(event._rawData, ["commit_id"], "")
                    }
                })
            if event_name == "closed":
                event_data.update({
                    "__typename": "ClosedEvent",
                    "id": dict_search(event._rawData, ["node_id"], ""),
                    "createdAt": dict_search(event._rawData, ["created_at"], ""),
                    "actor": None if event.actor is None else {
                        "id": dict_search(event._rawData, ["actor", "node_id"], ""),
                        "name": "",
                        "login": dict_search(event._rawData, ["actor", "login"], ""),
                        "email": ""
                    }
                })
            timeline.append(event_data)
        return timeline


class PullRequestReviews(RESTNode):
    """
    Collects pull request reviews with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, pull_request: PullRequest):
        super().__init__(github_rest_api)
        self.pull_request = pull_request
        self.review_comments = PullRequestReviewComments(self.get_github_rest_api(), pull_request).get_data()
        self.map_reply_to_id()

    def map_reply_to_id(self):
        """
        This is a quick fix to resolve the problem of pull request comments refering the reply_to field to the REST API
        id and the graphql API refering the relyTo id to the node_id
        """
        # TODO: Clean code
        # Create a mapping for review comments id -> node_id
        rawId_id_map = {
            "-1": None
        }
        # Insert mappings into list
        for review_comment in self.review_comments:
            rawId_id_map[str(review_comment.get("rawId"))] = str(review_comment.get("id"))
        # Map the reply to id field for each review comment from the REST API id to the GraphQL node_id
        for comment_id, comment in enumerate(self.review_comments):
            old_id = comment.get("replyTo", {}).get("id", "-1")
            new_id = rawId_id_map.get(old_id, None)
            self.review_comments[comment_id]["replyTo"]["id"] = new_id

    def get_data(self) -> []:
        reviews = []
        for review in self.get_github_rest_api().get_pull_request_reviews(self.pull_request):
            reviews.append(
                {
                    "id": dict_search(review._rawData, ["node_id"], ""),
                    "rawID": dict_search(review._rawData, ["id"], -1),
                    "state": dict_search(review._rawData, ["state"], "").upper(),
                    "body": dict_search(review._rawData, ["body"], ""),
                    "submittedAt": dict_search(review._rawData, ["submitted_at"], ""),
                    "createdAt": dict_search(review._rawData, ["submitted_at"], ""),
                    "author": None if review.user is None else {
                        "id": dict_search(review._rawData, ["user", "node_id"], ""),
                        "login": dict_search(review._rawData, ["user", "login"], ""),
                        "email": "",
                        "name": ""
                    },
                    "commit": {
                        "oid": dict_search(review._rawData, ["commit_id"], "")
                    },
                    "comments": {
                        "nodes": [
                            comment for comment in self.review_comments if comment.get("pullRequestReviewID") == review.id
                        ]
                    }
                }
            )
        return reviews


class PullRequestLabels(RESTNode):
    """
    Collects pull request labels with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, pull_request: PullRequest):
        super().__init__(github_rest_api)
        self.pull_request = pull_request

    def get_data(self) -> []:
        return [
            {
                "id": dict_search(label._rawData, ["node_id"], ""),
                "name": dict_search(label._rawData, ["name"], "")
            } for label in self.get_github_rest_api().get_pull_request_labels(self.pull_request)
        ]


class PullRequestComments(RESTNode):
    """
    Collects pull request comments with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, pull_request: PullRequest):
        super().__init__(github_rest_api)
        self.pull_request = pull_request

    def get_data(self) -> []:
        return [
            {
                "id": dict_search(comment._rawData, ["node_id"], ""),
                "body": dict_search(comment._rawData, ["body"], ""),
                "createdAt": dict_search(comment._rawData, ["created_at"], ""),
                "author": None if comment.user is None else {
                    "id": dict_search(comment._rawData, ["user", "node_id"], ""),
                    "login": dict_search(comment._rawData, ["user", "login"], ""),
                    "email": "",
                    "name": ""
                }
            } for comment in self.get_github_rest_api().get_pull_request_comments(self.pull_request)
        ]


class PullRequestFiles(RESTNode):
    """
    Collects pull request files with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, pull_request: PullRequest):
        super().__init__(github_rest_api)
        self.pull_request = pull_request

    def get_data(self) -> []:
        return [
            {
                "additions": dict_search(file._rawData, ["additions"], -1),
                "deletions": dict_search(file._rawData, ["deletions"], -1),
                "path": dict_search(file._rawData, ["filename"], ""),
                "changeType": dict_search(file._rawData, ["status"], "")
            } for file in self.get_github_rest_api().get_pull_request_files(self.pull_request)
        ]


class PullRequestAssignees(RESTNode):
    """
    Collects pull request assignees with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, pull_request: PullRequest):
        super().__init__(github_rest_api)
        self.pull_request = pull_request

    def get_data(self) -> []:
        assignees = dict_search(self.pull_request._rawData, ["assignees"], "")
        return [
            {
                "id": dict_search(assignee, ["node_id"], ""),
                "name": "",
                "login": dict_search(assignee, ["login"], ""),
                "email": ""
            } for assignee in assignees if dict_search(assignee, ["node_id"], "") != ""
        ]


class PullRequestRequestedReviewers(RESTNode):
    """
    Collects pull request requested reviewers with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, pull_request: PullRequest):
        super().__init__(github_rest_api)
        self.pull_request = pull_request

    def get_data(self) -> []:
        reviewers = dict_search(self.pull_request._rawData, ["requested_reviewers"], "")
        return [
            {
                "id": dict_search(reviewer, ["node_id"], ""),
                "name": "",
                "login": dict_search(reviewer, ["login"], ""),
                "email": ""
            } for reviewer in reviewers if dict_search(reviewer, ["node_id"], "") != ""
        ]


class PullRequestReviewComments(RESTNode):
    """
    Collects pull request review comments with the REST API
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper, pull_request: PullRequest):
        super().__init__(github_rest_api)
        self.pull_request = pull_request

    def get_data(self) -> []:
        return [
            {
                "pullRequestReviewID": dict_search(comment._rawData, ["pull_request_review_id"], -1),
                "id": dict_search(comment._rawData, ["node_id"], ""),
                "rawId": dict_search(comment._rawData, ["id"], ""),
                "body": dict_search(comment._rawData, ["body"], ""),
                "createdAt": dict_search(comment._rawData, ["created_at"], ""),
                "diffHunk": dict_search(comment._rawData, ["diff_hunk"], ""),
                "path": dict_search(comment._rawData, ["path"], ""),
                "startLine": dict_search(comment._rawData, ["start_line"], -1),
                "originalStartLine": dict_search(comment._rawData, ["original_start_line"], -1),
                "line": dict_search(comment._rawData, ["line"], -1),
                "originalLine": dict_search(comment._rawData, ["original_line"], -1),
                "author": None if comment.user is None else {
                    "id": dict_search(comment._rawData, ["user", "node_id"], ""),
                    "name": "",
                    "login": dict_search(comment._rawData, ["user", "login"], ""),
                    "email": "",
                },
                "replyTo": {
                    "id": str(dict_search(comment._rawData, ["in_reply_to_id"], "")),
                },
                "commit": {
                    "oid": dict_search(comment._rawData, ["commit_id"], "")
                },
                "originalCommit": {
                    "oid": dict_search(comment._rawData, ["original_commit_id"], "")
                }
            } for comment in self.get_github_rest_api().get_pull_request_review_comments(self.pull_request)
        ]


class PullRequestRoot(RESTRootNode):
    """
    Collects pull requests with the REST API
    """

    def get_data(self) -> dict:
        pull_request = self.get_github_rest_api().get_pull_request(self.get_node_number())
        # Construct pull request data
        return {
            "nodes": [
                {
                    "id": dict_search(pull_request._rawData, ["node_id"], ""),
                    "mergedAt": dict_search(pull_request._rawData, ["merged_at"], ""),
                    "number": dict_search(pull_request._rawData, ["number"], -1),
                    "title": dict_search(pull_request._rawData, ["title"], ""),
                    "body": dict_search(pull_request._rawData, ["body"], ""),
                    "isDraft": dict_search(pull_request._rawData, ["draft"], False),
                    "locked": dict_search(pull_request._rawData, ["locked"], False),
                    "createdAt": dict_search(pull_request._rawData, ["created_at"], ""),
                    "activeLockReason": dict_search(pull_request._rawData, ["active_lock_reason"], ""),
                    "state": dict_search(pull_request._rawData, ["state"], "").upper(),
                    "baseRepository": {
                        "id": dict_search(pull_request._rawData, ["base", "repo", "node_id"], None),
                        "url": dict_search(pull_request._rawData, ["base", "repo", "url"], "")
                    },
                    "headRepository": {
                        "id": dict_search(pull_request._rawData, ["head", "repo", "node_id"], None),
                        "url": dict_search(pull_request._rawData, ["head", "repo", "url"], "")
                    },
                    "headRefOid": dict_search(pull_request._rawData, ["head", "sha"], ""),
                    "headRefName": dict_search(pull_request._rawData, ["head", "ref"], None),
                    "baseRefOid": dict_search(pull_request._rawData, ["base", "sha"], ""),
                    "baseRefName": dict_search(pull_request._rawData, ["base", "ref"], None),
                    "author": None if pull_request.user is None else {
                        "id": dict_search(pull_request._rawData, ["user", "node_id"], ""),
                        "login": dict_search(pull_request._rawData, ["user", "login"], ""),
                        "email": "",
                        "name": ""
                    },
                    "reviewRequests": {
                        "nodes": PullRequestRequestedReviewers(self.get_github_rest_api(), pull_request).get_data()
                    },
                    "milestone": None if pull_request.milestone is None else {
                        "id": dict_search(pull_request._rawData, ["milestone", "node_id"], ""),
                        "number": dict_search(pull_request._rawData, ["milestone", "number"], -1),
                        "title": dict_search(pull_request._rawData, ["milestone", "title"], ""),
                        "description": dict_search(pull_request._rawData, ["milestone", "description"], ""),
                        "dueOn": dict_search(pull_request._rawData, ["milestone", "due_on"], ""),
                        "createdAt": dict_search(pull_request._rawData, ["milestone", "created_at"], ""),
                        "closedAt": dict_search(pull_request._rawData, ["milestone", "closed_at"], ""),
                        "progressPercentage": 100 * (pull_request.milestone.closed_issues / (
                                pull_request.milestone.open_issues + pull_request.milestone.closed_issues)),
                        "state": dict_search(pull_request._rawData, ["milestone", "state"], "").upper(),
                        "creator": None if pull_request.milestone.creator is None else {
                            "id": dict_search(pull_request._rawData, ["milestone", "creator", "node_id"], ""),
                            "login": dict_search(pull_request._rawData, ["milestone", "creator", "login"], ""),
                            "email": "",
                            "name": ""
                        }
                    },
                    "assignees": {
                        "nodes": PullRequestAssignees(self.get_github_rest_api(), pull_request).get_data()
                    },
                    "comments": {
                        "nodes": PullRequestComments(self.get_github_rest_api(), pull_request).get_data()
                    },
                    "timelineItems": {
                        "nodes": PullRequestTimeline(self.get_github_rest_api(), pull_request).get_data()
                    },
                    "reviews": {
                        "nodes": PullRequestReviews(self.get_github_rest_api(), pull_request).get_data()
                    },
                    "labels": {
                        "nodes": PullRequestLabels(self.get_github_rest_api(), pull_request).get_data()
                    },
                    "files": {
                        "nodes": PullRequestFiles(self.get_github_rest_api(), pull_request).get_data()
                    }
                }
            ]
        }
