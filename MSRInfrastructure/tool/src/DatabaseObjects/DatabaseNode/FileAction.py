from typing import Dict
from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE
from uuid import uuid4 as id_generator


class FileAction(DBNode):

    def __init__(self):
        self.data = {
            # ID is uniquely generated for each object
            "fileActionId": str(id_generator()),
            "changeType": "",
            "copiedFile": "",
            "renamedFile": "",
            "newFile": "",
            "deletedFile": "",
            "diff": "",
            "addedLines": "",
            "deletedLines": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "fileActionId": DATA_TYPE.STRING,
            "changeType": DATA_TYPE.STRING,
            "copiedFile": DATA_TYPE.BOOLEAN,
            "renamedFile": DATA_TYPE.BOOLEAN,
            "newFile": DATA_TYPE.BOOLEAN,
            "deletedFile": DATA_TYPE.BOOLEAN,
            "diff": DATA_TYPE.STRING,
            "addedLines": DATA_TYPE.INTEGER,
            "deletedLines": DATA_TYPE.INTEGER
        }

    def get_key_name(self) -> str:
        return "fileActionId"

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.FILE_ACTION

    def get_data(self) -> dict:
        return self.data
