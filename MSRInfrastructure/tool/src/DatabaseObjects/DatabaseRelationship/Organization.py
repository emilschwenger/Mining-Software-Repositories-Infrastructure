from typing import Dict
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE
from src.DatabaseObjects.DatabaseRelationship.DBRelationship import DBRelationship
from src.DatabaseObjects.DataTypes import DATA_TYPE


class OrganizationOwnsProject(DBRelationship):

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
        return RELATIONSHIP_TYPE.ORGANIZATION_OWNS_PROJECT

    def get_data(self) -> dict:
        return self.data
