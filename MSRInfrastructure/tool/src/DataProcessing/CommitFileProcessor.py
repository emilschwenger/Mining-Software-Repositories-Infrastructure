from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot
from src.DatabaseObjects.DatabaseNode.FileAction import FileAction
from src.DatabaseObjects.DatabaseNode.File import File
from src.DatabaseObjects.DatabaseNode.Commit import Commit
from src.DatabaseObjects.DatabaseRelationship.Commit import PerformsFileAction
from src.DatabaseObjects.DatabaseRelationship.FileAction import FileBeforeFileAction, FileAfterFileAction


class CommitFileProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        # Construct before file node
        file_before_node = File().extract_and_update({
            "mimeType": self.get_data().get("mimeTypeBefore", ""),
            "path": self.get_data().get("pathBefore", ""),
            "fileSha": self.get_data().get("fileShaBefore", ""),
            "fileSize": self.get_data().get("fileSizeBefore", -1),
        })
        file_before_node.extract_and_update({
            "fileId": file_before_node.hash_node()
        })
        self.get_repo().get_preprocessor_storage().add_node(file_before_node)
        # Construct after file node
        file_after_node = File().extract_and_update({
            "mimeType": self.get_data().get("mimeTypeAfter", ""),
            "path": self.get_data().get("pathAfter", ""),
            "fileSha": self.get_data().get("fileShaAfter", ""),
            "fileSize": self.get_data().get("fileSizeAfter", -1),
        })
        file_after_node.extract_and_update({
            "fileId": file_after_node.hash_node()
        })
        self.get_repo().get_preprocessor_storage().add_node(file_after_node)
        # Construct FileAction node
        file_action_node = FileAction().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(file_action_node)

        # Decide if a file needs the FILE_BEFORE/AFTER depending on if it is new or deleted
        new_file = self.get_data().get("newFile")
        deleted_file = self.get_data().get("deletedFile")
        if not new_file:
            # Construct relationship FileAction -[FILE_BEFORE_ACTION]-> File
            file_before_relationship = FileBeforeFileAction()
            file_before_relationship.set_source_node(file_action_node)
            file_before_relationship.set_destination_node(file_before_node)
            self.get_repo().get_preprocessor_storage().add_relationship(file_before_relationship)
        if not deleted_file:
            # Construct relationship FileAction -[FILE_AFTER_ACTION]-> File
            file_after_relationship = FileAfterFileAction()
            file_after_relationship.set_source_node(file_action_node)
            file_after_relationship.set_destination_node(file_after_node)
            self.get_repo().get_preprocessor_storage().add_relationship(file_after_relationship)

        # Construct relationship Commit -[PERFORMS_FILE_ACTION]-> FileAction
        # Construct commit node
        commit_node = Commit().extract_and_update({
            "hash": self.get_data().get("childCommitSha")
        })
        commit_performs_file_action_relationship = PerformsFileAction()
        commit_performs_file_action_relationship.set_source_node(commit_node)
        commit_performs_file_action_relationship.set_destination_node(file_action_node)
        self.get_repo().get_preprocessor_storage().add_relationship(commit_performs_file_action_relationship)
