from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class User(DBNode):

    def __init__(self):
        self.data = {
            "name": "",
            "login": "",
            "email": "",
            "id": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "name": DATA_TYPE.STRING,
            "login": DATA_TYPE.STRING,
            "email": DATA_TYPE.STRING,
            "id": DATA_TYPE.STRING
        }

    def can_merge(self) -> bool:
        return True

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.USER

    def get_data(self) -> dict:
        return self.data

    @staticmethod
    def get_default_user_data():
        return {
            "name": "default",
            "login": "default",
            "email": "default",
            "id": "default"
        }
