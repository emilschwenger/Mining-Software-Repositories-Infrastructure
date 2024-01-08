import os
import hashlib
import csv
import src.DatabaseObjects.DatabaseNode.DBNode as DBNode
import src.DatabaseObjects.DatabaseRelationship.DBRelationship as DBRelationship
from typing import Union
from src.DataProcessing.NodeType import NODE_TYPE
from src.DataProcessing.RelationshipType import RELATIONSHIP_TYPE


class RepositoryFileHandler:
    """
    RepositoryFileHandler manages and writes to repository CSV files. Every repository RepositoryCollector has its own
    instance.
    """

    def __init__(self, repo_owner: str, repo_name: str, deploy: bool = False):
        self.deploy = deploy
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def get_file_size(self):
        """
        Retrieve the file size of all repository CSV files
        :return: dict
        """
        file_sizes = {
            "nodes": {},
            "relationships": {}
        }
        for node in NODE_TYPE:
            file_path = self._get_file_name(node)
            file_exists = True if os.path.isfile(file_path) else False
            if file_exists:
                file_size = os.path.getsize(file_path) / (1024.0 ** 1)
                file_sizes.get("nodes").update({node.value: file_size})
            else:
                file_sizes.get("nodes").update({node.value: 0.0})
        for relationship in RELATIONSHIP_TYPE:
            file_path = self._get_file_name(relationship)
            file_exists = True if os.path.isfile(file_path) else False
            if file_exists:
                file_size = os.path.getsize(file_path) / (1024.0 ** 1)
                file_sizes.get("relationships").update({relationship.value: file_size})
            else:
                file_sizes.get("relationships").update({relationship.value: 0.0})
        return file_sizes

    def repo_to_hash(self):
        """
        Converts a combination of the repository owner and username into a unique hash
        """
        repo_id = self.repo_owner + "/" + self.repo_name
        hash_value = hashlib.sha256(repo_id.encode())
        return hash_value.hexdigest()

    def delete_files(self):
        """
        Deletes all CSV files corresponding to the repository
        """
        # Delete all NODE CSV files
        for node_type in NODE_TYPE:
            file_path = self._get_file_name(node_type)
            file_exists = True if os.path.isfile(file_path) else False
            if file_exists:
                os.remove(file_path)
        # Delete all RELATIONSHIP files
        for relationship_type in RELATIONSHIP_TYPE:
            file_path = self._get_file_name(relationship_type)
            file_exists = True if os.path.isfile(file_path) else False
            if file_exists:
                os.remove(file_path)

    def _get_file_name(self, file_type: Union[NODE_TYPE, RELATIONSHIP_TYPE]):
        """
        Constructs out of a node or relationship type a unique file name.
        :param file_type: NODE_TYPE or RELATIONSHIP_TYPE
        :return: file path
        """
        prefix = self.repo_to_hash()
        filename = prefix + "_" + str(file_type) + ".csv"
        file_location = "/repo_share/" if self.deploy else "./MSRInfrastructure/dev_data/repo_json/"
        return file_location + filename

    def get_file_name_neo4j(self, file_type: Union[NODE_TYPE, RELATIONSHIP_TYPE]):
        """
        Constructs out of a node or relationship type a unique file name in the Neo4J database format or None if
        the file does not exist.
        :param file_type: NODE_TYPE or RELATIONSHIP_TYPE
        :return: file path in the neo4j format 'file:///{filename}' or None if file does not exist
        """
        prefix = self.repo_to_hash()
        filename = prefix + "_" + str(file_type) + ".csv"
        file_location = "/repo_share/" if self.deploy else "./MSRInfrastructure/dev_data/repo_json/"
        file_exists = True if os.path.isfile(file_location + filename) else False
        if not file_exists:
            return None
        return "file:///" + filename

    def _append_to_file(self, content: dict, node_or_relationship_type: Union[NODE_TYPE, RELATIONSHIP_TYPE]):
        """
        Appends some content form a dictionary to a node or relationship CSV file.
        """
        file_path = self._get_file_name(node_or_relationship_type)
        # Check if the file already exists
        file_exists = True if os.path.isfile(file_path) else False
        # Append to the file
        with open(file_path, "a+", encoding="UTF-8", newline="") as f:
            # Construct CSV header in case file does not exist
            if not file_exists:
                csv_header = ",".join([column_name for column_name in content.keys()])
                f.write(csv_header + "\n")
            # Construct a csv writer instance
            repo_write = csv.writer(f, delimiter=",", quoting=csv.QUOTE_ALL, quotechar='"')
            # Construct data row
            repo_write.writerow([str(column) for column in content.values()])

    def append_relationship(self, relationship: DBRelationship):
        """
        Appends a DBRelationship and its content to a relationship CSV file.
        :param relationship: DBRelationship
        """
        # Append to CSV file
        content = {
            "source_id": relationship.get_unique_source_node_id(),
            "destination_id": relationship.get_unique_destination_node_id(),
        }
        if relationship.get_data() is not None:
            content.update(relationship.get_data())
        self._append_to_file(content, relationship.get_relationship_type())

    def append_node(self, node: DBNode):
        """
        Appends a DBNode and its content to a node CSV file.
        :param node: DBNode
        """
        # Append to CSV file
        self._append_to_file(
            content=node.get_data(),
            node_or_relationship_type=node.get_node_type()
        )
