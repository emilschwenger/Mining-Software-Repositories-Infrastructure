from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Language(DBNode):

    def __init__(self):
        self.data = {
            "name": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "name": DATA_TYPE.STRING
        }

    def get_key_name(self) -> str:
        return "name"

    def can_merge(self) -> bool:
        return True

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PROGRAMMING_LANGUAGE

    def get_data(self) -> dict:
        return self.data
