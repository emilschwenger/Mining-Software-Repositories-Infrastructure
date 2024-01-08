from abc import abstractmethod, ABC
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE
from typing import Optional, Dict
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DatabaseObjects.DataTypes import DATA_TYPE
import hashlib


class DBRelationship(ABC):
    """
    All relationships inherit this class that provides basic functionality.
    """

    def __init__(self):
        self.source: Optional[DBNode] = None
        self.destination: Optional[DBNode] = None

    def get_source_node(self) -> DBNode:
        return self.source

    def get_destination_node(self) -> DBNode:
        return self.destination

    def set_source_node(self, source: DBNode):
        self.source = source
        return self

    def set_destination_node(self, destination: DBNode):
        self.destination = destination
        return self

    def hash_relationship(self):
        """
        Hashes relationship source, destination nodes and  key/value attributes to unique value
        :return:
        """
        relationship_data = "|".join([key + ":" + str(value) for key, value in self.get_data().items()])
        hash_data = self.get_unique_source_node_id() + ":" + relationship_data + ":" + self.get_unique_destination_node_id()
        hash_value = hashlib.sha256(hash_data.encode())
        return hash_value.hexdigest()

    @abstractmethod
    def get_data(self):
        """
        Returns the data this node stores
        """
        pass

    @abstractmethod
    def get_relationship_type(self) -> RELATIONSHIP_TYPE:
        """
        Return the relationship type.
        """
        pass

    @abstractmethod
    def _get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        """
        Produces a dictionary where each value indicates the data type for its key value
        e.g., {"id": DATA_TYPE.STRING, "createdAt": DATA_TYPE.DATETIME}
        :return: dict
        """
        pass

    def get_relationship_name(self) -> str:
        """
        Returns the relationship name (Class name)
        :return: str
        """
        return self.__class__.__name__

    def has_properties(self) -> bool:
        """
        Returns true if the relationship has data properties
        :return: boolean
        """
        return len(self.get_data()) > 0

    def get_unique_source_node_id(self) -> str:
        """
        Return relationship source node ID and raises error if there is no source node
        """
        if self.source is None:
            raise Exception("[DB Relationship] Source node is none")
        return self.source.get_unique_node_id()

    def get_unique_destination_node_id(self) -> str:
        """
        Return relationship destination node ID and raises error if there is no destination node
        """
        if self.destination is None:
            raise Exception("[DB Relationship] Destination node is none")
        return self.destination.get_unique_node_id()

    def _update(self, update_values: dict):
        """
        Updates the node data dictionary with update_values
        """
        self.get_data().update(update_values)

    def extract_and_update(self, data: dict):
        """
        Extract all key value properties from data and extract all values from all keys in data that are also
        existent in the node data.
        :param data: new data dictionary
        """
        update_dict = {}
        for key, value in data.items():
            if value is None or isinstance(value, list) or isinstance(value, dict):
                continue
            if key in self.get_data().keys():
                update_dict[key] = value
        self._update(update_dict)

    def get_cypher_properties(self):
        """
        Constructs a string in the format 'x: row.x, y: row.y, ...' to adequately format node properties in a Cypher query.
        This is necessary to formulate Neo4J Cypher queries
        :return: str
        """
        def format_single_property(property_name, property_type: DATA_TYPE):
            if property_type == DATA_TYPE.FLOAT:
                return property_name + ": CASE row." + property_name + " WHEN null THEN toFloat('-1') WHEN '' THEN toFloat('-1') ELSE toFloat(row." + property_name + ") END"
            elif property_type == DATA_TYPE.DATETIME:
                return property_name + ": CASE row." + property_name + " WHEN null THEN datetime('0001-01-01T01:01:01Z') WHEN '' THEN datetime('0001-01-01T01:01:01Z') ELSE datetime(row." + property_name + ") END"
            elif property_type == DATA_TYPE.BOOLEAN:
                return property_name + ": CASE row." + property_name + " WHEN 'True' THEN true WHEN 'False' THEN false ELSE false END"
            elif property_type == DATA_TYPE.INTEGER:
                return property_name + ": CASE row." + property_name + " WHEN null THEN toInteger('-1') WHEN '' THEN toInteger('-1') ELSE toInteger(row." + property_name + ") END"
            elif property_type == DATA_TYPE.STRING:
                return property_name + ": CASE row." + property_name + " WHEN null THEN '' ELSE row." + property_name + " END"
            else:
                raise Exception(f"[DB Node] Resolving datatype of {property_name} ({property_type.value}) not possible")
        keys = [format_single_property(key, self._get_cypher_property_type().get(key, None)) for key in self.get_data().keys()]
        return ", ".join(keys)
