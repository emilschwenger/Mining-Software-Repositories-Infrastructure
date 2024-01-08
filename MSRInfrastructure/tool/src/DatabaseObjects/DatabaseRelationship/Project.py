from typing import Dict
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE
from src.DatabaseObjects.DatabaseRelationship.DBRelationship import DBRelationship
from src.DatabaseObjects.DataTypes import DATA_TYPE


class ProjectHasBranch(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PROJECT_HAS_BRANCH

    def get_data(self) -> dict:
        return self.data


class ProjectContainsLanguage(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CONTAINS_LANGUAGE

    def get_data(self) -> dict:
        return self.data


class ProjectIsDependentOn(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.DEPENDENT_ON

    def get_data(self) -> dict:
        return self.data


class ProjectIsLicensed(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.IS_LICENSED

    def get_data(self) -> dict:
        return self.data


class ProjectHasWorkflow(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.HAS_WORKFLOW

    def get_data(self) -> dict:
        return self.data


class ProjectHasMilestone(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PROJECT_HAS_MILESTONE

    def get_data(self) -> dict:
        return self.data


class ProjectHasRelease(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.HAS_RELEASE

    def get_data(self) -> dict:
        return self.data


class ProjectHasLabel(DBRelationship):
    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PROJECT_HAS_LABEL

    def get_data(self) -> dict:
        return self.data


class ProjectHasTopic(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.HAS_TOPIC

    def get_data(self) -> dict:
        return self.data


class ProjectHasDiscussion(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PROJECT_HAS_DISCUSSION

    def get_data(self) -> dict:
        return self.data


class ProjectHasCommitMonth(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "date_month": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "date_month": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.HAS_COMMIT_MONTH

    def get_data(self) -> dict:
        return self.data


class ProjectHasPullRequestMonth(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "date_month": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "date_month": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.HAS_PULL_REQUEST_MONTH

    def get_data(self) -> dict:
        return self.data


class ProjectHasIssueMonth(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {
            "date_month": ""
        }

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "date_month": DATA_TYPE.DATETIME
        }

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.HAS_ISSUE_MONTH

    def get_data(self) -> dict:
        return self.data
