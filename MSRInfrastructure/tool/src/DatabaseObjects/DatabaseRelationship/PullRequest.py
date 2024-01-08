from typing import Dict
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE
from src.DatabaseObjects.DatabaseRelationship.DBRelationship import DBRelationship
from src.DatabaseObjects.DataTypes import DATA_TYPE


class PullRequestHasEvent(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_HAS_EVENT

    def get_data(self) -> dict:
        return self.data


class PullRequestEventLinksCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_EVENT_LINKS_COMMIT

    def get_data(self) -> dict:
        return self.data


class PullRequestHasLabel(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_HAS_LABEL

    def get_data(self) -> dict:
        return self.data


class RequestsReviewer(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.REQUESTS_REVIEWER

    def get_data(self) -> dict:
        return self.data


class PullRequestInMonth(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_IN_MONTH

    def get_data(self) -> dict:
        return self.data


class IsReplyToPullRequestReviewComment(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.REPLY_TO_PULL_REQUEST_REVIEW_COMMENT

    def get_data(self) -> dict:
        return self.data


class PullRequestReviewCommentCommentsCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_REVIEW_COMMENT_COMMENTS_COMMIT

    def get_data(self) -> dict:
        return self.data


class PullRequestReviewCommentCommentsOriginalCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_REVIEW_COMMENT_COMMENTS_ORIGINAL_COMMIT

    def get_data(self) -> dict:
        return self.data


class IsSinglePullRequestReviewComment(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.IS_SINGLE_PULL_REQUEST_REVIEW_COMMENT

    def get_data(self) -> dict:
        return self.data


class IsPullRequestBaseCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.IS_PULL_REQUEST_BASE_COMMIT

    def get_data(self) -> dict:
        return self.data


class IsPullRequestHeadCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.IS_PULL_REQUEST_HEAD_COMMIT

    def get_data(self) -> dict:
        return self.data


class CommentsOnPullRequestReview(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.COMMENTS_ON_PULL_REQUEST_REVIEW

    def get_data(self) -> dict:
        return self.data


class PullRequestReviewReviewsCommit(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_REVIEW_REVIEWS_COMMIT

    def get_data(self) -> dict:
        return self.data


class PullRequestHasReview(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_HAS_REVIEW

    def get_data(self) -> dict:
        return self.data


class PullRequestProposesFileChange(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_PROPOSES_CHANGE

    def get_data(self) -> dict:
        return self.data


class PullRequestHasSourceBranch(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_HAS_SOURCE_BRANCH

    def get_data(self) -> dict:
        return self.data


class PullRequestHasTargetBranch(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PULL_REQUEST_HAS_TARGET_BRANCH

    def get_data(self) -> dict:
        return self.data
