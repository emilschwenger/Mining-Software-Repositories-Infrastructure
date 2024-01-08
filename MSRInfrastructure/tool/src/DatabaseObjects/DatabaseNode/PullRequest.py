from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class PullRequest(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "number": "",
            "mergedAt": "",
            "title": "",
            "body": "",
            "isDraft": "",
            "locked": "",
            "activeLockReason": "",
            "state": "",
            "baseRepositoryURL": "",
            "headRepositoryURL": "",
            "baseRefOid": "",
            "headRefOid": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "number": DATA_TYPE.INTEGER,
            "mergedAt": DATA_TYPE.DATETIME,
            "title": DATA_TYPE.STRING,
            "body": DATA_TYPE.STRING,
            "isDraft": DATA_TYPE.BOOLEAN,
            "locked": DATA_TYPE.BOOLEAN,
            "activeLockReason": DATA_TYPE.STRING,
            "state": DATA_TYPE.STRING,
            "baseRepositoryURL": DATA_TYPE.STRING,
            "headRepositoryURL": DATA_TYPE.STRING,
            "baseRefOid": DATA_TYPE.STRING,
            "headRefOid": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PULL_REQUEST

    def get_data(self) -> dict:
        return self.data


class ProjectPullRequestMonth(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "year": "",
            "month": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "year": DATA_TYPE.INTEGER,
            "month": DATA_TYPE.INTEGER
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PROJECT_PULL_REQUEST_MONTH

    def get_data(self) -> dict:
        return self.data


class PullRequestEvent(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "__typename": "",
            "additionalData": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "__typename": DATA_TYPE.STRING,
            "additionalData": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PULL_REQUEST_EVENT

    def get_data(self) -> dict:
        return self.data


class PullRequestFile(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            # Pull Request ID added to this node for unique identification in combination with content
            "pullRequestId": "",
            "sha": "",
            "path": "",
            "changeType": "",
            "additions": "",
            "deletions": "",
            "changes": "",
            "patch": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            # Pull Request ID added to this node for unique identification in combination with content
            "pullRequestId": DATA_TYPE.STRING,
            "sha": DATA_TYPE.STRING,
            "path": DATA_TYPE.STRING,
            "changeType": DATA_TYPE.STRING,
            "additions": DATA_TYPE.INTEGER,
            "deletions": DATA_TYPE.INTEGER,
            "changes": DATA_TYPE.INTEGER,
            "patch": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PULL_REQUEST_FILE

    def get_unique_node_id(self) -> str:
        return self.update_node_id()

    def update_node_id(self) -> str:
        # Calculate the id based on all node content except for the id itself
        self.get_data()["id"] = ""
        node_id = self.hash_node()
        self.get_data()["id"] = node_id
        return node_id

    def get_data(self) -> dict:
        return self.data


class PullRequestReview(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "state": "",
            "body": "",
            "createdAt": "",
            "submittedAt": "",
            "commitHash": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "state": DATA_TYPE.STRING,
            "body": DATA_TYPE.STRING,
            "createdAt": DATA_TYPE.DATETIME,
            "submittedAt": DATA_TYPE.DATETIME,
            "commitHash": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PULL_REQUEST_REVIEW

    def get_data(self) -> dict:
        return self.data


class PullRequestReviewComment(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "rawId": "",
            "body": "",
            "diffHunk": "",
            "path": "",
            "startLine": "",
            "originalStartLine": "",
            "line": "",
            "originalLine": "",
            "commitHash": "",
            "originalCommitHash": "",
            "replyToId": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "rawId": DATA_TYPE.INTEGER,
            "body": DATA_TYPE.STRING,
            "diffHunk": DATA_TYPE.STRING,
            "path": DATA_TYPE.STRING,
            "startLine": DATA_TYPE.INTEGER,
            "originalStartLine": DATA_TYPE.INTEGER,
            "line": DATA_TYPE.INTEGER,
            "originalLine": DATA_TYPE.INTEGER,
            "commitHash": DATA_TYPE.STRING,
            "originalCommitHash": DATA_TYPE.STRING,
            "replyToId": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PULL_REQUEST_REVIEW_COMMENT

    def get_data(self) -> dict:
        return self.data
