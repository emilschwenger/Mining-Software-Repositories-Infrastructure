from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Discussion(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "number": "",
            "title": "",
            "closed": "",
            "closedAt": "",
            "upvoteCount": "",
            "body": "",
            "categoryName": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "number": DATA_TYPE.INTEGER,
            "title": DATA_TYPE.STRING,
            "closed": DATA_TYPE.BOOLEAN,
            "closedAt": DATA_TYPE.DATETIME,
            "upvoteCount": DATA_TYPE.INTEGER,
            "body": DATA_TYPE.STRING,
            "categoryName": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.DISCUSSION

    def get_data(self) -> dict:
        return self.data


class DiscussionComment(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "body": "",
            "isAnswer": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "body": DATA_TYPE.STRING,
            "isAnswer": DATA_TYPE.BOOLEAN
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.DISCUSSION_COMMENT

    def get_data(self) -> dict:
        return self.data
