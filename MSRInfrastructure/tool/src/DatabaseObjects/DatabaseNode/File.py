from typing import Dict
from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class File(DBNode):

    def __init__(self):
        self.data = {
            # fileId has to be manually calculated by calling self.hash_node() with all properties except the fileId
            "fileId": "",
            "mimeType": "",
            "path": "",
            "fileSha": "",
            "fileSize": -1
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "fileId": DATA_TYPE.STRING,
            "mimeType": DATA_TYPE.STRING,
            "path": DATA_TYPE.STRING,
            "fileSha": DATA_TYPE.STRING,
            "fileSize": DATA_TYPE.INTEGER
        }

    def get_key_name(self) -> str:
        return "fileId"

    def can_merge(self) -> bool:
        return True

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.FILE

    def get_data(self) -> dict:
        return self.data
