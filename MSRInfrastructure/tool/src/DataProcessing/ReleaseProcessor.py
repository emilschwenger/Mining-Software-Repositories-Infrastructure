from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot, ProcessorTemplate
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.Commit import Commit
from src.DatabaseObjects.DatabaseNode.Release import Release
from src.DatabaseObjects.DatabaseRelationship.User import CreatesRelease
from src.DatabaseObjects.DatabaseRelationship.Release import ReleaseTagsCommit
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasRelease

class ReleaseProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        for release in self.get_data().get("nodes", []):
            if release is None:
                continue
            single_release = ReleaseProcessor(self.get_repo(), release, self)
            single_release.process()


class ReleaseProcessor(ProcessorTemplate):
    def process(self):
        # Construct release node
        release_node = Release().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(release_node)

        # Construct Project -[HAS_RELEASE]-> Release
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        project_release_relationship = ProjectHasRelease()
        project_release_relationship.set_source_node(project_node)
        project_release_relationship.set_destination_node(release_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_release_relationship)

        # Process tagged commit data
        commit_data = self.get_data().get("tagCommit", {}).get("oid", None)
        if commit_data is not None and len(commit_data) > 0:
            # Construct commit node
            commit_node = Commit().extract_and_update({
                "hash": commit_data
            })
            # Construct release -[TAGS_COMMIT]-> commit relationship
            release_commit_relationship = ReleaseTagsCommit()
            release_commit_relationship.set_source_node(release_node)
            release_commit_relationship.set_destination_node(commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(release_commit_relationship)

        # Construct author node
        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)

        # construct user -[CREATES_RELEASE]-> release relationship
        author_release_relationship = CreatesRelease()
        author_release_relationship.set_source_node(author_node)
        author_release_relationship.set_destination_node(release_node)
        author_release_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_release_relationship)
