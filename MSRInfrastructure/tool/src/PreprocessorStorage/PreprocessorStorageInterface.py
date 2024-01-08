from src.PreprocessorStorage.RepositoryContainer import RepositoryContainer
from src.PreprocessorStorage.RepositoryFileHandler import RepositoryFileHandler
from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from src.DatabaseObjects.DatabaseRelationship.DBRelationship import DBRelationship
from typing import Union
from src.DataProcessing.NodeType import NODE_TYPE
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE


class PreprocessorStorageInterface:
    """
    Interface for interacting and modifying the in-memory repository version and repository CSV files.
    """

    def __init__(self, repo_owner: str, repo_name: str, deploy: bool = False):
        self.deploy = deploy
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self._file_handler = RepositoryFileHandler(repo_owner=repo_owner, repo_name=repo_name, deploy=deploy)
        self._repository_container = RepositoryContainer()

    def get_file_size(self):
        """
        Retrieve the file size of all repository files
        :return: dict
        """
        return self._file_handler.get_file_size()

    def delete_all_files(self):
        """
        Deletes all files corresponding to this repository mining process
        :return:
        """
        self._file_handler.delete_files()

    def get_file_name_neo4j(self, file_type: Union[NODE_TYPE, RELATIONSHIP_TYPE]):
        """
        Generates file path in the neo4j format 'file:///{filename}' or None if file does not exist
        :param file_type:
        :return:
        """
        return self._file_handler.get_file_name_neo4j(file_type)

    def add_node(self, node: DBNode):
        """
        Adds a node to the in memory storage and write the node into a CSV file
        :param node: DBNode
        """
        # Return if the node exists already
        node_exists = self._repository_container.node_exists(node)
        if node_exists:
            return
        # Write the node into CSV file and in memory storage
        self._file_handler.append_node(node)
        self._repository_container.add_node(node)

    def add_relationship(self, relationship: DBRelationship):
        """
        Adds a hashed relationships to the in memory storage and write the relationship into a CSV file
        :param relationship: DBRelationship
        """
        # Return if the relationship exists already
        relationship_exists = self._repository_container.relationship_exists(relationship)
        if relationship_exists:
            # If relationship exists we skip it
            return
        # If relationship does not exist write the node into CSV file and in memory storage
        self._file_handler.append_relationship(relationship)
        self._repository_container.add_relationship(relationship)

    def get_branch_id(self, project_id: str, branch_name: str):
        """
        Constructs out of the branch name and project id a unique node id
        :return: node_id
        """
        return self._repository_container.get_branch_id(project_id, branch_name)

    def get_issue_time_aggregator_id(self, time: str):
        """
        Constructs out of a time string a unique issue time aggregation node id
        :param time: Expects time in the format 'YYYY-MM-DDTHH:MM:SSZ'
        :return: the uuid of the issue time aggregator node
        """
        return self._repository_container.get_issue_time_aggregator_id(time)

    def get_pull_request_time_aggregator_id(self, time: str):
        """
        Constructs out of a time string a unique pull request time aggregation node id
        :param time: Expects time in the format 'YYYY-MM-DDTHH:MM:SSZ'
        :return: the uuid of the pull request time aggregator node
        """
        return self._repository_container.get_pull_request_time_aggregator_id(time)

    def get_commit_time_aggregator_id(self, time: str):
        """
        Constructs out of a time string a unique commit time aggregation node id
        :param time: Expects time in the format 'YYYY-MM-DDTHH:MM:SSZ'
        :return: the uuid of the commit time aggregator node
        """
        return self._repository_container.get_commit_time_aggregator_id(time)
