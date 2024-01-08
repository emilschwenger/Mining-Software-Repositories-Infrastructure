from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Issue(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "number": "",
            "title": "",
            "body": "",
            "state": "",
            "convertedToDiscussion": False
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "number": DATA_TYPE.INTEGER,
            "title": DATA_TYPE.STRING,
            "body": DATA_TYPE.STRING,
            "state": DATA_TYPE.STRING,
            "convertedToDiscussion": DATA_TYPE.BOOLEAN
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.ISSUE

    def get_data(self) -> dict:
        return self.data


class ProjectIssueMonth(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "year": "",
            "month": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "year": DATA_TYPE.INTEGER,
            "month": DATA_TYPE.INTEGER
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PROJECT_ISSUE_MONTH

    def get_data(self) -> dict:
        return self.data
