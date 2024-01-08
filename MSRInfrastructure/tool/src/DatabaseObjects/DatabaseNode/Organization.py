from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Organization(DBNode):

    def __init__(self):
        self.data = {
            "orgId": "",
            "organizationEmail": "",
            "orgDesc": "",
            "orgLogin": "",
            "orgName": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "orgId": DATA_TYPE.STRING,
            "organizationEmail": DATA_TYPE.STRING,
            "orgDesc": DATA_TYPE.STRING,
            "orgLogin": DATA_TYPE.STRING,
            "orgName": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.ORGANIZATION

    def get_key_name(self) -> str:
        return "orgId"

    def can_merge(self) -> bool:
        return True

    def get_data(self) -> dict:
        return self.data
