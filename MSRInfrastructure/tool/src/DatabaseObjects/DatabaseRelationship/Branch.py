from typing import Dict
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE
from src.DatabaseObjects.DatabaseRelationship.DBRelationship import DBRelationship
from src.DatabaseObjects.DataTypes import DATA_TYPE


class BranchHeadCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.BRANCH_HAS_HEAD_COMMIT

    def get_data(self) -> dict:
        return self.data


class BranchContainsCommit(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.CONTAINS_COMMIT

    def get_data(self) -> dict:
        return self.data
