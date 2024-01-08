from src.DatabaseObjects.DatabaseNode.DBNode import DBNode
from uuid import uuid4
from src.DatabaseObjects.DatabaseRelationship.DBRelationship import DBRelationship


class RepositoryContainer:
    """
    RepositoryContainer manages the in memory version of a repository.
    """

    def __init__(self):
        # Node and relationship container store ID's content hashes to determine if a node or relationship already exist
        self.repository_node_container = {}
        self.repository_relationship_container = {}
        # ID's for the time aggregation nodes as they have no unique ID from GitHub
        self.time_aggregator_ids = {
            "issue": {},
            "pullRequest": {},
            "commit": {}
        }
        # ID's for the branch nodes as they have no unique ID from GitHub
        self.branch_ids = {}

    def get_branch_id(self, project_id: str, branch_name: str):
        """
        Constructs out of the branch and project name a unique node id
        :return: node_id
        """
        key = project_id + branch_name
        if key not in self.branch_ids.keys():
            self.branch_ids[key] = str(uuid4())
        return self.branch_ids[key]

    def get_issue_time_aggregator_id(self, time: str):
        """
        Constructs out of the first seven characters of a time string a unique node id. The first seven characters
        show year and month.
        :return: node_id
        """
        if time[:7] not in self.time_aggregator_ids["issue"].keys():
            self.time_aggregator_ids["issue"][time[:7]] = str(uuid4())
        return self.time_aggregator_ids["issue"][time[:7]]

    def get_pull_request_time_aggregator_id(self, time: str):
        """
        Constructs out of the first seven characters of a time string a unique node id. The first seven characters
        show year and month.
        :return: node_id
        """
        if time[:7] not in self.time_aggregator_ids["pullRequest"].keys():
            self.time_aggregator_ids["pullRequest"][time[:7]] = str(uuid4())
        return self.time_aggregator_ids["pullRequest"][time[:7]]

    def get_commit_time_aggregator_id(self, time: str):
        """
        Constructs out of the first seven characters of a time string a unique node id. The first seven characters
        show year and month.
        :return: node_id
        """
        if time[:7] not in self.time_aggregator_ids["commit"].keys():
            self.time_aggregator_ids["commit"][time[:7]] = str(uuid4())
        return self.time_aggregator_ids["commit"][time[:7]]

    def add_relationship(self, relationship: DBRelationship):
        """
        Add source node ID and relationship hash to the in memory repository relationships
        Why hash? between the same node ids sometimes multiple relationships exist and relationship content is
        included in the hashed value
        """
        source_node = relationship.get_source_node()
        source_node_id = source_node.get_unique_node_id()
        relationship_hash = relationship.hash_relationship()
        relationship_type = relationship.get_relationship_type()

        # Create relationship dictionary if it is not existent
        if relationship_type not in self.repository_relationship_container.keys():
            self.repository_relationship_container[relationship_type] = {}
        # Retrieve current relationship container and append relationship
        relationship_type_container = self.repository_relationship_container[relationship_type]
        if relationship.get_source_node().get_unique_node_id() in relationship_type_container.keys():
            relationship_type_container[source_node_id].append(relationship_hash)
        else:
            relationship_type_container[source_node_id] = [relationship_hash]

    def add_node(self, node: DBNode):
        """
        Appends a node to the in memory repository version
        """
        if node.get_node_type().value not in self.repository_node_container:
            self.repository_node_container[node.get_node_type().value] = [node.get_unique_node_id()]
        else:
            self.repository_node_container[node.get_node_type().value].append(node.get_unique_node_id())

    def node_exists(self, node: DBNode):
        """
        Returns true if a node already exists
        """
        if node.get_node_type().value in self.repository_node_container:
            if node.get_unique_node_id() in self.repository_node_container[node.get_node_type().value]:
                return True
        return False

    def relationship_exists(self, relationship: DBRelationship):
        """
        Returns true if a relationship already exists
        """
        source_node = relationship.get_source_node()
        source_node_id = source_node.get_unique_node_id()
        relationship_hash = relationship.hash_relationship()
        relationship_type = relationship.get_relationship_type()

        # Check if relationship dictionary for this relationship type is not existent
        if relationship_type not in self.repository_relationship_container.keys():
            return False
        # Check if the relationship exists withing the relationship type container
        relationship_type_container = self.repository_relationship_container[relationship_type]
        if source_node_id in relationship_type_container.keys():
            if relationship_hash in relationship_type_container[source_node_id]:
                return True
        return False
