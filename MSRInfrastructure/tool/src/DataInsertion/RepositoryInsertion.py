from neo4j import GraphDatabase, Driver
from typing import Optional

import src.RepositoryCollector as RepositoryCollector
from src.Utility.Logger import MSRLogger
from src.Utility.Utility import read_config
from src.DatabaseObjects.DataTypes import DATA_TYPE

from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.Label import Label
from src.DatabaseObjects.DatabaseNode.Topic import Topic
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseNode.Milestone import Milestone
from src.DatabaseObjects.DatabaseNode.Organization import Organization
from src.DatabaseObjects.DatabaseNode.Release import Release
from src.DatabaseObjects.DatabaseNode.File import File
from src.DatabaseObjects.DatabaseNode.FileAction import FileAction
from src.DatabaseObjects.DatabaseNode.Workflow import Workflow, WorkflowRun
from src.DatabaseObjects.DatabaseNode.License import License
from src.DatabaseObjects.DatabaseNode.Language import Language
from src.DatabaseObjects.DatabaseNode.Issue import Issue, ProjectIssueMonth
from src.DatabaseObjects.DatabaseNode.Discussion import Discussion, DiscussionComment
from src.DatabaseObjects.DatabaseNode.Dependency import Dependency
from src.DatabaseObjects.DatabaseNode.Commit import Commit, ProjectCommitMonth
from src.DatabaseObjects.DatabaseNode.Branch import Branch
from src.DatabaseObjects.DatabaseNode.PullRequest import PullRequest, PullRequestFile, PullRequestReview, \
    PullRequestEvent, PullRequestReviewComment, ProjectPullRequestMonth

from src.DatabaseObjects.DatabaseRelationship.Branch import BranchHeadCommit, BranchContainsCommit
from src.DatabaseObjects.DatabaseRelationship.Commit import CommitInMonth, PerformsFileAction, ParentOf
from src.DatabaseObjects.DatabaseRelationship.Discussion import DiscussionHasComment, ReplyToDiscussionComment, \
    DiscussionHasLabel, CommentAnswersDiscussion
from src.DatabaseObjects.DatabaseRelationship.FileAction import FileAfterFileAction, FileBeforeFileAction
from src.DatabaseObjects.DatabaseRelationship.Issue import IssueInMonth, IssueHasLabel
from src.DatabaseObjects.DatabaseRelationship.Milestone import RequiresIssue, RequiresPullRequest
from src.DatabaseObjects.DatabaseRelationship.Organization import OrganizationOwnsProject
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasIssueMonth, ProjectHasPullRequestMonth, \
    ProjectHasCommitMonth, ProjectHasRelease, ProjectHasLabel, ProjectHasWorkflow, ProjectHasMilestone, \
    ProjectHasTopic, ProjectHasBranch, ProjectIsLicensed, ProjectIsDependentOn, ProjectContainsLanguage, \
    ProjectHasDiscussion
from src.DatabaseObjects.DatabaseRelationship.PullRequest import PullRequestHasLabel, PullRequestInMonth, \
    RequestsReviewer, CommentsOnPullRequestReview, PullRequestProposesFileChange, \
    IsReplyToPullRequestReviewComment, IsPullRequestBaseCommit, IsPullRequestHeadCommit, PullRequestEventLinksCommit, \
    PullRequestHasReview, PullRequestHasEvent, IsSinglePullRequestReviewComment, PullRequestReviewReviewsCommit, \
    PullRequestReviewCommentCommentsOriginalCommit, PullRequestReviewCommentCommentsCommit, \
    PullRequestHasTargetBranch, PullRequestHasSourceBranch
from src.DatabaseObjects.DatabaseRelationship.Release import ReleaseTagsCommit
from src.DatabaseObjects.DatabaseRelationship.User import AuthorOfCommit, CommitterOfCommit, ClosesIssue, \
    CommentsOnIssue, CreatesIssue, CreatesPullRequest, CreatesDiscussion, \
    CommentsOnCommit, CommentsOnPullRequest, CreatesPullRequestEvent, \
    TriggersWorkflowRun, UserOwnsProject, CreatesRelease, CreatesDiscussionComment, \
    CreatesWorkflowRun, CreatesPullRequestReview, CreatesMilestone, CreatesPullRequestReviewComment, \
    StarsProject, GetsAssignedIssue, GetsAssignedPullRequest, WatchesProject
from src.DatabaseObjects.DatabaseRelationship.Workflow import HasWorkflowRun
from src.DatabaseObjects.DatabaseRelationship.WorkflowRun import WorkflowRunHasHeadCommit


class RepositoryInsertion:
    """
    RepositoryInsertion is responsible for establishing a connection to the database and generating and executing
    all queries to insert nodes and relationships from CSV files
    """
    def __init__(self, repo: RepositoryCollector):
        self.logger = MSRLogger.get_logger(self.__class__.__name__)
        self.config = read_config()
        self.project_id = repo.get_project_id()
        self.IP = "neo4j1" if repo.is_deployment() else "localhost"
        self.URI = f"bolt://{self.IP}:7687"
        self.db: Optional[Driver] = None
        self.repo_owner = repo.get_repo_owner()
        self.repo_name = repo.get_repo_name()
        self.repo = repo

    def start(self):
        """
        Starts the process of inserting all collected CSV files into the Neo4J database.
        """
        print(f"{self.repo_name}/{self.repo_owner} Start inserting repository into database")
        self.connect()
        self.create_indexes()
        self.insert_nodes()
        self.insert_relationships()
        self.link_nodes_to_issues_and_pull_requests()
        self.link_pull_request_file_and_merge_commit_file()
        self.disconnect()

    def connect(self):
        """
        Establishment of the connection to the Neo4J database
        """
        self.db = GraphDatabase.driver(uri=self.URI, auth=(self.config.get("db_username"), self.config.get("db_password")))
        self.logger.info(f"{self.repo_owner}/{self.repo_name} Connection to Neo4J established")

    def disconnect(self):
        """
        Disconnecting from the Neo4J database
        """
        self.db.close()
        self.logger.info(f"{self.repo_owner}/{self.repo_name} Connection to Neo4J closed")

    def create_indexes(self):
        """
        Creating database indexes for every unique node identification property/ node time properties/ relationship
        time properties
        """
        self.logger.info(f"{self.repo_owner}/{self.repo_name} Creating database indexes")

        node_types = RepositoryInsertion.initialize_placeholder_nodes()
        for node in node_types:
            node_name = node.get_node_name()
            self.create_node_index(node.get_node_type().value + "_indices", node_name, node.get_key_name())

            # Index time properties for every node
            for property_name, property_value in node.get_cypher_property_type().items():
                if property_value == DATA_TYPE.DATETIME:
                    self.create_node_index(node.get_node_type().value + "_" + property_name + "_indices", node_name, property_name)

        # Index time properties for every relationship
        relationship_types = RepositoryInsertion.initialize_placeholder_relationships()
        for relationship in relationship_types:
            relationship_name = relationship.get_relationship_type().value
            for property_name, property_value in relationship._get_cypher_property_type().items():
                if property_value == DATA_TYPE.DATETIME:
                    self.create_relationship_index(relationship_name + "_" + property_name + "_indices", relationship_name, property_name)

    def create_node_index(self, index_name, node_label, key_name):
        """
        Executes query to create an index on a node property
        """
        with self.db.session() as t:
            t.run(f"CREATE INDEX {index_name} IF NOT EXISTS FOR (n:{node_label}) ON (n.{key_name})")

    def create_relationship_index(self, index_name, relationship_label, key_name):
        """
        Executes query to create an index on a relationship property
        """
        with self.db.session() as t:
            t.run(f"CREATE INDEX {index_name} IF NOT EXISTS FOR ()-[r:{relationship_label}]-() ON (r.{key_name})")

    def insert_nodes(self):
        """
        Loops over all repository node CSV files to generate and execute a Cypher insertion query
        """
        node_types = RepositoryInsertion.initialize_placeholder_nodes()
        # Loop over all node types
        for node_type in node_types:
            self.logger.info(f"{self.repo_owner}/{self.repo_name} Inserting node {node_type.get_node_type().value}")
            # Retrieve file path and check if the file exists
            file_path = self.repo.get_preprocessor_storage().get_file_name_neo4j(node_type.get_node_type())
            if file_path is None:
                continue
            # Insert all nodes
            node_name = node_type.get_node_name()
            properties = node_type.get_cypher_properties()
            operator = "MERGE" if node_type.can_merge() else "CREATE"
            query_result = self.run_query(f"""
            LOAD CSV WITH HEADERS FROM '{file_path}' AS row
            CALL{{
                WITH row
                {operator} (:{node_name} {{{properties}}})
            }} IN TRANSACTIONS OF 300 ROWS
            """)

    def insert_relationships(self):
        """
        Loops over all repository relationship CSV files to generate and execute a Cypher insertion query
        """
        relationship_types = RepositoryInsertion.initialize_placeholder_relationships()
        # Loop over all relationship types
        for relationship_type in relationship_types:
            self.logger.info(f"{self.repo_owner}/{self.repo_name} Inserting relationship {relationship_type.get_relationship_type().value}")
            # Retrieve file path and check if the file exists
            file_path = self.repo.get_preprocessor_storage().get_file_name_neo4j(
                relationship_type.get_relationship_type())
            if file_path is None:
                continue
            # Insert all relationships
            source_node_name = relationship_type.get_source_node().get_node_name()
            source_node_key = relationship_type.get_source_node().get_key_name()
            destination_node_name = relationship_type.get_destination_node().get_node_name()
            destination_node_key = relationship_type.get_destination_node().get_key_name()
            properties = relationship_type.get_cypher_properties()
            relationship_name = relationship_type.get_relationship_type().value
            if relationship_type.has_properties():
                query_result = self.run_query(f"""
                LOAD CSV WITH HEADERS FROM '{file_path}' AS row
                CALL{{
                    WITH row
                    MATCH (s:{source_node_name} {{{source_node_key}: row.source_id}})
                    MATCH (d:{destination_node_name} {{{destination_node_key}: row.destination_id}})
                    CREATE (s)-[:{relationship_name} {{{properties}}}]->(d)
                }} IN TRANSACTIONS OF 300 ROWS
                """)
            else:
                query_result = self.run_query(f"""
                LOAD CSV WITH HEADERS FROM '{file_path}' AS row
                CALL{{
                    WITH row
                    MATCH (s:{source_node_name} {{{source_node_key}: row.source_id}})
                    MATCH (d:{destination_node_name} {{{destination_node_key}: row.destination_id}})
                    WITH s, d
                    CREATE (s)-[:{relationship_name}]->(d)
                }} IN TRANSACTIONS OF 300 ROWS
                """)

    def run_query(self, query: str):
        """
        Executes a Cypher query
        Note: This method closes the session before result consumption is possible. If result consumption is
        necessary, it is required to create a custom method and consume the result before closing session.
        e.g., with session() as s:
                result = s.run(query)
                .. work with result
        """
        with self.db.session() as t:
            return t.run(query)

    def link_nodes_to_issues_and_pull_requests(self):
        """
        Executes a query to connect every node in a repository that has the attribute title, message, or body and
        contains a link to another number in the form of 'fixes #234' or only '#234' to its respective issue.
        """
        self.logger.info(f"{self.repo_owner}/{self.repo_name} Establishing issue/pull request links")
        self.run_query(f"""
        MATCH (p:Project {{id: '{self.repo.get_project_id()}'}})
        CALL apoc.path.subgraphAll(p,{{
        labelFilter: '-Topic|-File|-Language|-Dependency|-User|-License|-Branch|-File'
        }})
        YIELD nodes as nodes_list
        UNWIND nodes_list as n
        UNWIND apoc.text.regexGroups(n.message,
            '.*(?i)(?:(fix|close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)? #(\\d+)).*') +
        apoc.text.regexGroups(n.title, 
            '.*(?i)(?:(fix|close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)? #(\\d+)).*') +
        apoc.text.regexGroups(n.body, 
            '.*(?i)(?:(fix|close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)? #(\\d+)).*') as g
        WITH n, g
        WHERE size(g) > 0
        CALL {{
            WITH n, g
            MATCH (:Project {{id: '{self.repo.get_project_id()}'}})-[:HAS_PULL_REQUEST_MONTH]->(pprm:ProjectPullRequestMonth),
            (pprm)<-[:PULL_REQUEST_IN_MONTH]-(pr:PullRequest)
            WHERE pr.number = toInteger(g[2])
            CREATE (n)-[:LINKS_PULL_REQUEST {{action: CASE g[1] WHEN null THEN "NO_ACTION" ELSE toString(g[1]) END}}]->(pr)
        }}
        CALL {{
            WITH n, g
            MATCH (:Project {{id: '{self.repo.get_project_id()}'}})-[:HAS_ISSUE_MONTH]->(pim:ProjectIssueMonth),
            (pim)<-[:ISSUE_IN_MONTH]-(i:Issue)
            WHERE i.number = toInteger(g[2])
            CREATE (n)-[:LINKS_ISSUE {{action: CASE g[1] WHEN null THEN "NO_ACTION" ELSE toString(g[1]) END}}]->(i)
        }}
        """)

    def link_pull_request_file_and_merge_commit_file(self):
        """
        Executes a query to link a pull request file to its corresponding file node after the pull request merge
        """
        self.logger.info(f"{self.repo_owner}/{self.repo_name} Linking pull request files to file nodes")
        self.run_query(f"""
        MATCH (p:Project {{id: '{self.repo.get_project_id()}'}})-[:HAS_PULL_REQUEST_MONTH]->(prm:ProjectPullRequestMonth)<-[:PULL_REQUEST_IN_MONTH]-(pr:PullRequest)-[:PROPOSES_CHANGE]->(prf:PullRequestFile),
        (pr)-[:HAS_EVENT]->(pre:PullRequestEvent {{__typename: 'MergedEvent'}})-[:LINKS_COMMIT]->(c:Commit)-[:PERFORMS]->(fc:FileAction)-[:AFTER_ACTION]->(f:File)
        WHERE f.path = prf.path
        CREATE (prf)-[:FILE_AFTER_MERGE]->(f)
        """)

    @staticmethod
    def initialize_placeholder_nodes():
        """
        Initializes an instance of all database nodes to facilitate looping over all types
        """
        return [
            Branch(), Dependency(), Discussion(), DiscussionComment(), File(), FileAction(), Issue(),
            ProjectIssueMonth(), Label(), Language(), License(), Milestone(), Organization(), Project(), PullRequest(),
            PullRequestFile(), PullRequestReviewComment(), PullRequestEvent(), PullRequestReview(),
            ProjectPullRequestMonth(), Commit(), ProjectCommitMonth(), Release(), Topic(), User(), Workflow(),
            WorkflowRun()
        ]

    @staticmethod
    def initialize_placeholder_relationships():
        """
        Initializes an instance of all database relationships to facilitate looping over all types
        """
        return [
            BranchHeadCommit().set_source_node(Branch()).set_destination_node(Commit()),
            CommitInMonth().set_source_node(Commit()).set_destination_node(ProjectCommitMonth()),
            PerformsFileAction().set_source_node(Commit()).set_destination_node(FileAction()),
            ParentOf().set_source_node(Commit()).set_destination_node(Commit()),
            DiscussionHasComment().set_source_node(Discussion()).set_destination_node(DiscussionComment()),
            ReplyToDiscussionComment().set_source_node(DiscussionComment()).set_destination_node(DiscussionComment()),
            DiscussionHasLabel().set_source_node(Discussion()).set_destination_node(Label()),
            CommentAnswersDiscussion().set_source_node(DiscussionComment()).set_destination_node(Discussion()),
            FileAfterFileAction().set_source_node(FileAction()).set_destination_node(File()),
            FileBeforeFileAction().set_source_node(FileAction()).set_destination_node(File()),
            IssueInMonth().set_source_node(Issue()).set_destination_node(ProjectIssueMonth()),
            IssueHasLabel().set_source_node(Issue()).set_destination_node(Label()),
            RequiresIssue().set_source_node(Milestone()).set_destination_node(Issue()),
            RequiresPullRequest().set_source_node(Milestone()).set_destination_node(PullRequest()),
            OrganizationOwnsProject().set_source_node(Organization()).set_destination_node(Project()),
            ProjectHasIssueMonth().set_source_node(Project()).set_destination_node(ProjectIssueMonth()),
            ProjectHasPullRequestMonth().set_source_node(Project()).set_destination_node(ProjectPullRequestMonth()),
            ProjectHasCommitMonth().set_source_node(Project()).set_destination_node(ProjectCommitMonth()),
            ProjectHasRelease().set_source_node(Project()).set_destination_node(Release()),
            ProjectHasLabel().set_source_node(Project()).set_destination_node(Label()),
            ProjectHasWorkflow().set_source_node(Project()).set_destination_node(Workflow()),
            ProjectHasMilestone().set_source_node(Project()).set_destination_node(Milestone()),
            ProjectHasTopic().set_source_node(Project()).set_destination_node(Topic()),
            ProjectHasBranch().set_source_node(Project()).set_destination_node(Branch()),
            ProjectIsLicensed().set_source_node(Project()).set_destination_node(License()),
            ProjectIsDependentOn().set_source_node(Project()).set_destination_node(Dependency()),
            ProjectContainsLanguage().set_source_node(Project()).set_destination_node(Language()),
            PullRequestHasLabel().set_source_node(PullRequest()).set_destination_node(Label()),
            PullRequestInMonth().set_source_node(PullRequest()).set_destination_node(ProjectPullRequestMonth()),
            RequestsReviewer().set_source_node(PullRequest()).set_destination_node(User()),
            CommentsOnPullRequestReview().set_source_node(PullRequestReviewComment()).set_destination_node(PullRequestReview()),
            IsReplyToPullRequestReviewComment().set_source_node(PullRequestReviewComment()).set_destination_node(PullRequestReviewComment()),
            IsPullRequestBaseCommit().set_source_node(PullRequest()).set_destination_node(Commit()),
            IsPullRequestHeadCommit().set_source_node(PullRequest()).set_destination_node(Commit()),
            PullRequestEventLinksCommit().set_source_node(PullRequestEvent()).set_destination_node(Commit()),
            PullRequestHasReview().set_source_node(PullRequest()).set_destination_node(PullRequestReview()),
            PullRequestHasEvent().set_source_node(PullRequest()).set_destination_node(PullRequestEvent()),
            IsSinglePullRequestReviewComment().set_source_node(PullRequestReviewComment()).set_destination_node(PullRequest()),
            PullRequestProposesFileChange().set_source_node(PullRequest()).set_destination_node(PullRequestFile()),
            ReleaseTagsCommit().set_source_node(Release()).set_destination_node(Commit()),
            AuthorOfCommit().set_source_node(User()).set_destination_node(Commit()),
            CommitterOfCommit().set_source_node(User()).set_destination_node(Commit()),
            ClosesIssue().set_source_node(User()).set_destination_node(Issue()),
            CommentsOnIssue().set_source_node(User()).set_destination_node(Issue()),
            CreatesIssue().set_source_node(User()).set_destination_node(Issue()),
            CreatesPullRequest().set_source_node(User()).set_destination_node(PullRequest()),
            CreatesDiscussion().set_source_node(User()).set_destination_node(Discussion()),
            CommentsOnCommit().set_source_node(User()).set_destination_node(Commit()),
            CommentsOnPullRequest().set_source_node(User()).set_destination_node(PullRequest()),
            CreatesPullRequestEvent().set_source_node(User()).set_destination_node(PullRequestEvent()),
            TriggersWorkflowRun().set_source_node(User()).set_destination_node(WorkflowRun()),
            UserOwnsProject().set_source_node(User()).set_destination_node(Project()),
            CreatesRelease().set_source_node(User()).set_destination_node(Release()),
            CreatesDiscussionComment().set_source_node(User()).set_destination_node(DiscussionComment()),
            CreatesWorkflowRun().set_source_node(User()).set_destination_node(WorkflowRun()),
            CreatesPullRequestReview().set_source_node(User()).set_destination_node(PullRequestReview()),
            CreatesMilestone().set_source_node(User()).set_destination_node(Milestone()),
            CreatesPullRequestReviewComment().set_source_node(User()).set_destination_node(PullRequestReviewComment()),
            StarsProject().set_source_node(User()).set_destination_node(Project()),
            GetsAssignedIssue().set_source_node(User()).set_destination_node(Issue()),
            GetsAssignedPullRequest().set_source_node(User()).set_destination_node(PullRequest()),
            WatchesProject().set_source_node(User()).set_destination_node(Project()),
            HasWorkflowRun().set_source_node(Workflow()).set_destination_node(WorkflowRun()),
            WorkflowRunHasHeadCommit().set_source_node(WorkflowRun()).set_destination_node(Commit()),
            PullRequestReviewReviewsCommit().set_source_node(PullRequestReview()).set_destination_node(Commit()),
            PullRequestReviewCommentCommentsCommit().set_source_node(PullRequestReviewComment()).set_destination_node(Commit()),
            PullRequestReviewCommentCommentsOriginalCommit().set_source_node(PullRequestReviewComment()).set_destination_node(Commit()),
            PullRequestHasTargetBranch().set_source_node(PullRequest()).set_destination_node(Branch()),
            PullRequestHasSourceBranch().set_source_node(PullRequest()).set_destination_node(Branch()),
            ProjectHasDiscussion().set_source_node(Project()).set_destination_node(Discussion()),
            BranchContainsCommit().set_source_node(Branch()).set_destination_node(Commit())
        ]
