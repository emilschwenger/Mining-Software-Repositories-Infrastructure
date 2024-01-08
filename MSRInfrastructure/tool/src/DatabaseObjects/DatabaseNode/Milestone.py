from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Milestone(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "number": "",
            "title": "",
            "description": "",
            "dueOn": "",
            "closedAt": "",
            "progressPercentage": "",
            "state": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "number": DATA_TYPE.INTEGER,
            "title": DATA_TYPE.STRING,
            "description": DATA_TYPE.STRING,
            "dueOn": DATA_TYPE.DATETIME,
            "closedAt": DATA_TYPE.DATETIME,
            "progressPercentage": DATA_TYPE.FLOAT,
            "state": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.MILESTONE

    def get_data(self) -> dict:
        return self.data
