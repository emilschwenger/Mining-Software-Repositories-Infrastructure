from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot, ProcessorTemplate
from src.DatabaseObjects.DatabaseNode.Commit import Commit, ProjectCommitMonth
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseRelationship.Commit import CommitInMonth, ParentOf
from src.DatabaseObjects.DatabaseRelationship.User import AuthorOfCommit, CommitterOfCommit, CommentsOnCommit
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasCommitMonth
from git import Commit as GitPythonCommit
from datetime import datetime


class CommitContentProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        commit_data: GitPythonCommit = self.get_data()["commit"]

        # Construct Commit node
        commit_node = Commit().extract_and_update({
            "hash": commit_data.hexsha,
            "message": commit_data.message,
            "merge": len(commit_data.parents) > 1
        })
        self.get_repo().get_preprocessor_storage().add_node(commit_node)
        self.set_node(commit_node)

        # Construct commit time aggregator node
        committed_time = commit_data.committed_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        commit_time_aggregator_node_id = self.get_repo().get_preprocessor_storage().get_commit_time_aggregator_id(
            time=committed_time
        )
        project_commit_month_node = ProjectCommitMonth().extract_and_update({
            "id": commit_time_aggregator_node_id,
            "year": commit_data.committed_datetime.year,
            "month": commit_data.committed_datetime.month
        })
        self.get_repo().get_preprocessor_storage().add_node(project_commit_month_node)

        # Construct commit -[COMMIT_IN_MONTH]-> ProjectCommitMonth relationship
        commit_in_month_relationship = CommitInMonth().set_source_node(commit_node).set_destination_node(
            project_commit_month_node
        )
        self.get_repo().get_preprocessor_storage().add_relationship(commit_in_month_relationship)

        # Construct Project -[HAS_COMMIT_MONTH]-> ProjectCommitMonth
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        project_commit_month_relationship = ProjectHasCommitMonth()
        project_commit_month_relationship.set_source_node(project_node)
        project_commit_month_relationship.set_destination_node(project_commit_month_node)
        project_commit_month_relationship.extract_and_update({
            "date_month": datetime(
                commit_data.committed_datetime.year,
                commit_data.committed_datetime.month,
                1).strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        self.get_repo().get_preprocessor_storage().add_relationship(project_commit_month_relationship)

        # Construct Commit -[PARENT_OF]-> Commit
        for parent in commit_data.parents:
            parent_commit_node = Commit().extract_and_update({"hash": parent.hexsha})
            commit_parent_relationship = ParentOf().set_source_node(parent_commit_node).set_destination_node(
                commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(commit_parent_relationship)


class CommitMetaProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        # Construct commit node
        commit_hash = self.get_data().get("hash")
        commit_node = Commit().extract_and_update({"hash": commit_hash})
        self.set_node(commit_node)
        # Process author data
        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        # Construct author node
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)
        # Construct user -[AUTHOR_OF]-> Commit
        author_commit_relationship = AuthorOfCommit()
        author_commit_relationship.set_source_node(author_node)
        author_commit_relationship.set_destination_node(commit_node)
        author_commit_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_commit_relationship)

        # Process committer data
        committer_data = self.get_data().get("committer", None)
        if committer_data is None:
            committer_data = User.get_default_user_data()
        # Construct committer node
        committer_node = User().extract_and_update(committer_data)
        self.get_repo().get_preprocessor_storage().add_node(committer_node)
        # Construct user -[COMMITTER_OF]-> Commit
        committer_commit_relationship = CommitterOfCommit()
        committer_commit_relationship.set_source_node(committer_node)
        committer_commit_relationship.set_destination_node(commit_node)
        committer_commit_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(committer_commit_relationship)

        # Process commit comments
        commit_comments_data = self.get_data().get("commitComments", [])
        for commit_comment in commit_comments_data:
            commit_comment_processor = CommitCommentProcessor(self.get_repo(), commit_comment, self)
            commit_comment_processor.process()


class CommitCommentProcessor(ProcessorTemplate):
    def process(self):
        # Create commit comment author node
        author_data = self.get_data().get("user", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        # Construct author node
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)
        # Construct Relationship author -[COMMENTS_ON_COMMIT]-> Commit
        author_comment_relationship = CommentsOnCommit()
        author_comment_relationship.set_source_node(author_node)
        author_comment_relationship.set_destination_node(self.get_parent().get_node())
        author_comment_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_comment_relationship)
