from typing import Dict
from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Dependency(DBNode):

    def __init__(self):
        self.data = {
            "name": "",
            "versionInfo": "",
            "nameAndVersion": "",
            "licenseDeclared": "",
            "dev": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "name": DATA_TYPE.STRING,
            "versionInfo": DATA_TYPE.STRING,
            "nameAndVersion": DATA_TYPE.STRING,
            "licenseDeclared": DATA_TYPE.STRING,
            "dev": DATA_TYPE.BOOLEAN
        }

    def get_key_name(self) -> str:
        return "nameAndVersion"

    def can_merge(self) -> bool:
        return True

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.DEPENDENCY

    def get_data(self) -> dict:
        return self.data
