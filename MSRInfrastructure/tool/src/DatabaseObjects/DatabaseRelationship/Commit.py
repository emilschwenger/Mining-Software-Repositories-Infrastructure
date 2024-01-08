from typing import Dict
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE
from src.DatabaseObjects.DatabaseRelationship.DBRelationship import DBRelationship
from src.DatabaseObjects.DataTypes import DATA_TYPE


class PerformsFileAction(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PERFORMS_FILE_ACTION

    def get_data(self) -> dict:
        return self.data


class CommitInMonth(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.COMMIT_IN_MONTH

    def get_data(self) -> dict:
        return self.data


class ParentOf(DBRelationship):

    def __init__(self):
        super().__init__()
        self.data = {}

    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {}

    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        return RELATIONSHIP_TYPE.PARENT_OF

    def get_data(self) -> dict:
        return self.data
