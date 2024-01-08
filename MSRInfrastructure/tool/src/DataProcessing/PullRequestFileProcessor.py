from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot
from src.DatabaseObjects.DatabaseNode.PullRequest import PullRequestFile, PullRequest
from src.DatabaseObjects.DatabaseRelationship.PullRequest import PullRequestProposesFileChange


class PullRequestFileProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        # Construct Pull Request node
        pull_request_id = self.get_data().get("pullRequestId", None)
        # Edge case
        if pull_request_id is None:
            return
        pull_request_node = PullRequest().extract_and_update({"id": pull_request_id})
        # Construct Pull Request File node
        file_node = PullRequestFile().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(file_node)

        # Construct PullRequest -[PROPOSES_CHANGE]-> PullRequestFileChange Relationship
        pull_request_file_relationship = PullRequestProposesFileChange()
        pull_request_file_relationship.set_source_node(pull_request_node)
        pull_request_file_relationship.set_destination_node(file_node)
        self.get_repo().get_preprocessor_storage().add_relationship(pull_request_file_relationship)
