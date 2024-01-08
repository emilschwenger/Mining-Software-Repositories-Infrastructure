from typing import Dict
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE
from src.DatabaseObjects.DatabaseRelationship.DBRelationship import DBRelationship
from src.DatabaseObjects.DataTypes import DATA_TYPE


class GetsAssignedIssue(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.GETS_ASSIGNED_ISSUE

    def get_data(self) -> dict:
        return self.data


class GetsAssignedPullRequest(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.GETS_ASSIGNED_PULL_REQUEST

    def get_data(self) -> dict:
        return self.data


class CreatesIssue(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_ISSUE

    def get_data(self) -> dict:
        return self.data


class ClosesIssue(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "id": "",
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CLOSES_ISSUE

    def get_data(self) -> dict:
        return self.data


class CommentsOnIssue(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "id": "",
            "createdAt": "",
            "body": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "createdAt": DATA_TYPE.DATETIME,
            "body": DATA_TYPE.STRING
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.COMMENTS_ON_ISSUE

    def get_data(self) -> dict:
        return self.data


class CreatesMilestone(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": "",
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_MILESTONE

    def get_data(self) -> dict:
        return self.data


class UserOwnsProject(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.USER_OWNS_PROJECT

    def get_data(self) -> dict:
        return self.data


class CreatesPullRequest(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_PULL_REQUEST

    def get_data(self) -> dict:
        return self.data


class CommentsOnPullRequest(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {
            "id": "",
            "body": "",
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "body": DATA_TYPE.STRING,
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.COMMENTS_ON_PULL_REQUEST

    def get_data(self) -> dict:
        return self.data


class CreatesPullRequestEvent(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_PULL_REQUEST_EVENT

    def get_data(self) -> dict:
        return self.data


class CreatesPullRequestReviewComment(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_PULL_REQUEST_REVIEW_COMMENT

    def get_data(self) -> dict:
        return self.data


class CreatesDiscussion(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_DISCUSSION

    def get_data(self) -> dict:
        return self.data


class CreatesDiscussionComment(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_DISCUSSION_COMMENT

    def get_data(self) -> dict:
        return self.data


class CreatesRelease(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_RELEASE

    def get_data(self) -> dict:
        return self.data


class CommitterOfCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "committedAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "committedAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.COMMITTER_OF

    def get_data(self) -> dict:
        return self.data


class AuthorOfCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "authoredAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "authoredAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.AUTHOR_OF

    def get_data(self) -> dict:
        return self.data


class StarsProject(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.STARS

    def get_data(self) -> dict:
        return self.data


class WatchesProject(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.WATCHES

    def get_data(self) -> dict:
        return self.data


class CreatesPullRequestReview(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_PULL_REQUEST_REVIEW

    def get_data(self) -> dict:
        return self.data


class CreatesWorkflowRun(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CREATES_WORKFLOW_RUN

    def get_data(self) -> dict:
        return self.data


class TriggersWorkflowRun(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "startedAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "startedAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.TRIGGERS_WORKFLOW_RUN

    def get_data(self) -> dict:
        return self.data


class CommentsOnCommit(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {
            "id": "",
            "body": "",
            "path": "",
            "position": "",
            "line": "",
            "createdAt": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "body": DATA_TYPE.STRING,
            "path": DATA_TYPE.STRING,
            "position": DATA_TYPE.INTEGER,
            "line": DATA_TYPE.INTEGER,
            "createdAt": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.COMMENTS_ON_COMMIT

    def get_data(self) -> dict:
        return self.data
