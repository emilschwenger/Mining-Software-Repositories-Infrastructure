from typing import Dict
from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Commit(DBNode):

    def __init__(self):
        self.data = {
            "hash": "",
            "message": "",
            "merge": "",
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "hash": DATA_TYPE.STRING,
            "message": DATA_TYPE.STRING,
            "merge": DATA_TYPE.BOOLEAN,
        }

    def get_key_name(self) -> str:
        return "hash"

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.COMMIT

    def get_data(self) -> dict:
        return self.data


class ProjectCommitMonth(DBNode):

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
        return NODE_TYPE.PROJECT_COMMIT_MONTH

    def get_data(self) -> dict:
        return self.data
