from abc import abstractmethod, ABC
from typing import Dict
from src.DataProcessing.NodeType import NODE_TYPE
from src.DatabaseObjects.DataTypes import DATA_TYPE
import hashlib
from src.Utility.Utility import check_string, check_boolean, check_datetime, check_number_int, check_number_float

class DBNode(ABC):
    """
    All nodes inherit this class that provides basic functionality.
    """

    def hash_node(self):
        """
        Hashes node key and value attributes to unique value
        :return:
        """
        node_data = "|".join([key + ":" + str(value) for key, value in self.get_data().items()])
        hash_value = hashlib.sha256(node_data.encode())
        return hash_value.hexdigest()

    @abstractmethod
    def get_node_type(self) -> NODE_TYPE:
        pass

    def get_unique_node_id(self) -> str:
        return self.get_data().get(self.get_key_name())

    @abstractmethod
    def get_data(self) -> dict:
        pass

    def can_merge(self) -> bool:
        """
        True if the node can be merged across multiple repositories (e.g., Topics/Languages/...) (DEFAULT: False)
        :return: bool
        """
        return False

    def get_key_name(self) -> str:
        """
        Returns the node specific unique key (DEFAULT: 'id')
        :return: str
        """
        return "id"

    def has_properties(self) -> bool:
        """
        Determines if the node has data properties
        :return: boolean
        """
        return len(self.get_data()) > 0

    def get_node_name(self):
        """
        Returns the node name (Class name)
        :return: str
        """
        return self.__class__.__name__

    def _update(self, update_values: dict):
        self.get_data().update(update_values)
        return self

    def _check_data_value(self, value, data_type: DATA_TYPE):
        """
        Check an arbitrary value according to its data type
        """
        if data_type == DATA_TYPE.INTEGER:
            return check_number_int(value)
        elif data_type == DATA_TYPE.FLOAT:
            return check_number_float(value)
        elif data_type == DATA_TYPE.STRING:
            return check_string(value)
        elif data_type == DATA_TYPE.BOOLEAN:
            return check_boolean(value)
        elif data_type == DATA_TYPE.DATETIME:
            return check_datetime(value)
        else:
            return check_string(value)

    def extract_and_update(self, data: dict):
        """
        Extract all key value properties from data and extract all values from all keys in data that are also
        existent in the node data.
        :param attribute_keys: str of attribute keys to extract from
        :param data: data dictionary
        """
        update_dict = {}
        for key, value in data.items():
            if value is None or isinstance(value, list) or isinstance(value, dict):
                continue
            if key in self.get_data().keys():
                new_value_datatype = self.get_cypher_property_type().get(key, None)
                if new_value_datatype is None:
                    raise Exception(f"[DBNode] Datatype for key {key} not found")
                update_dict[key] = self._check_data_value(value, new_value_datatype)
        self._update(update_dict)
        return self

    @abstractmethod
    def get_cypher_property_type(self) -> Dict[str, DATA_TYPE]:
        """
        Returns a dictionary of DATA_TYPE values for each node property
        """
        pass

    def get_cypher_properties(self, include=None):
        """
        Constructs a string in the format 'x: row.x, y: row.y, ...' to adequately format node properties in a Cypher query.
        This is necessary to formulate Cypher queries
        :include a list of key values to include from the data dictionary | if none include all
        :return: str
        """
        def format_single_property(property_name, property_type: DATA_TYPE):
            if include is not None and property_name not in include:
                return None
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
        keys = []
        for key in self.get_data().keys():
            property_query_string = format_single_property(key, self.get_cypher_property_type().get(key, None))
            if property_query_string is not None:
                keys.append(property_query_string)
        return ", ".join(keys)