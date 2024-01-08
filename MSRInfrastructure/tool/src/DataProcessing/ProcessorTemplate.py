from abc import ABC, abstractmethod
# from src.RepositoryCollector import RepositoryCollector
import src.RepositoryCollector as RepositoryCollector
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from typing import Optional


class ProcessorTemplateRoot(ABC):
    """
    All data processors on the first layer inherit from this class. It provides basic functionality to facilitate
    processing in a hierarchical structure.
    """
    def __init__(self, repo: RepositoryCollector, data: dict):
        self._repo = repo
        self._data = data
        self._node: Optional[DBNode] = None

    @abstractmethod
    def process(self):
        pass

    def get_node_id(self):
        return self._node.get_unique_node_id()

    def get_node(self):
        return self._node

    def set_node(self, node: DBNode):
        self._node = node

    def get_repo(self) -> RepositoryCollector:
        return self._repo

    def get_data(self) -> dict:
        return self._data


class ProcessorTemplate(ProcessorTemplateRoot, ABC):
    """
    All data processors on the second or below layer inherit from this class. It provides basic functionality to
    facilitate processing in a hierarchical structure.
    """

    def __init__(self, repo: RepositoryCollector, data: dict, parent):
        super().__init__(repo, data)
        self._parent = parent

    def get_parent(self):
        return self._parent
