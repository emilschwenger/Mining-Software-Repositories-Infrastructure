from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.Branch import Branch
from src.DatabaseObjects.DatabaseNode.Commit import Commit
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasBranch
from src.DatabaseObjects.DatabaseRelationship.Branch import BranchHeadCommit, BranchContainsCommit


class BranchProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        # Construct Head Commit node
        head_commit_node = Commit().extract_and_update({"hash": self.get_data()["headCommitSha"]})

        # Construct Project node
        project_node = Project().extract_and_update({"id": self.get_repo().get_project_id()})
        self.get_repo().get_preprocessor_storage().add_node(project_node)

        # Construct Branch node
        branch_name = self.get_data()["branchName"].name
        branch_node = Branch().extract_and_update({
            "id": self.get_repo().get_preprocessor_storage().get_branch_id(
                self.get_repo().get_project_id(),
                branch_name
            ),
            "name": branch_name
        })
        self.get_repo().get_preprocessor_storage().add_node(branch_node)

        # Construct Project -[HAS_BRANCH]-> Branch Relationship
        project_branch_relationship = ProjectHasBranch()
        project_branch_relationship.set_source_node(project_node)
        project_branch_relationship.set_destination_node(branch_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_branch_relationship)

        # Construct Branch -[BRANCH_HAS_HEAD_COMMIT]-> Commit Relationship
        branch_head_commit = BranchHeadCommit().set_source_node(branch_node).set_destination_node(head_commit_node)
        self.get_repo().get_preprocessor_storage().add_relationship(branch_head_commit)

        # Connect Commits to Branch
        for commit in self.get_data().get("branchCommits", []):
            # Construct Commit node
            branch_commit_node = Commit().extract_and_update({"hash": commit})
            # Construct Commit
            branch_commit_relationship = BranchContainsCommit()
            branch_commit_relationship.set_source_node(branch_node)
            branch_commit_relationship.set_destination_node(branch_commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(branch_commit_relationship)
