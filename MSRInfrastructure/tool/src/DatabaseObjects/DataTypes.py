from enum import Enum


class DATA_TYPE(Enum):
    """
    A list of data types that the infrastructure can insert into the Neo4J database.
    """
    STRING = "STRING"
    DATETIME = "DATETIME"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
