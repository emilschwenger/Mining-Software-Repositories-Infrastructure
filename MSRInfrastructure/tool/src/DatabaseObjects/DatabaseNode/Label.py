from typing import Dict
from src.DatabaseObjects.DataTypes import DATA_TYPE
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DataProcessing.NodeType import NODE_TYPE


class Label(DBNode):

    def __init__(self):
        self.data = {
            "id": "",
            "name": ""
        }

    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        return {
            "id": DATA_TYPE.STRING,
            "name": DATA_TYPE.STRING
        }

    def get_node_type(self) -> NODE_TYPE:
        return NODE_TYPE.LABEL

    def get_data(self) -> dict:
        return self.data
