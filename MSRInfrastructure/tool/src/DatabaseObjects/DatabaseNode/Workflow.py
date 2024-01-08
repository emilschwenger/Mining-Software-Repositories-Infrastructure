from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Workflow(DBNode):

    def __init__(self):
        self.data = {
                "id": "",
                "title": "",
                "configPath": "",
                "createdAt": "",
                "state": "",
                "headCommit": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "title": DATA_TYPE.STRING,
            "configPath": DATA_TYPE.STRING,
            "createdAt": DATA_TYPE.DATETIME,
            "state": DATA_TYPE.STRING,
            "headCommit": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.WORKFLOW

    def get_data(self) -> dict:
        return self.data


class WorkflowRun(DBNode):

    def __init__(self):
        self.data = {
                "id": "",
                "status": "",
                "conclusion": "",
                "attempts": "",
                "state": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "status": DATA_TYPE.STRING,
            "conclusion": DATA_TYPE.STRING,
            "attempts": DATA_TYPE.INTEGER,
            "state": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.WORKFLOW_RUN

    def get_data(self) -> dict:
        return self.data
