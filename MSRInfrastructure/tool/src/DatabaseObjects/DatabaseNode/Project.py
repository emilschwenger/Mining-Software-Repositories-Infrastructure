from typing import Dict

from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Project(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "url": "",
            "name": "",
            "description": "",
            "isArchived": "",
            "archivedAt": "",
            "isMirror": "",
            "mirrorUrl": "",
            "isLocked": "",
            "lockReason": "",
            "diskUsage": "",
            "visibility": "",
            "forkingAllowed": "",
            "hasWikiEnabled": "",
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "url": DATA_TYPE.STRING,
            "name": DATA_TYPE.STRING,
            "description": DATA_TYPE.STRING,
            "isArchived": DATA_TYPE.BOOLEAN,
            "archivedAt": DATA_TYPE.DATETIME,
            "isMirror": DATA_TYPE.BOOLEAN,
            "mirrorUrl": DATA_TYPE.STRING,
            "isLocked": DATA_TYPE.BOOLEAN,
            "lockReason": DATA_TYPE.STRING,
            "diskUsage": DATA_TYPE.INTEGER,
            "visibility": DATA_TYPE.STRING,
            "forkingAllowed": DATA_TYPE.BOOLEAN,
            "hasWikiEnabled": DATA_TYPE.BOOLEAN
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.PROJECT

    def get_data(self) -> dict:
        return self.data

