from src.DataProcessing.ProcessorTemplate import ProcessorTemplate, ProcessorTemplateRoot
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.License import License
from src.DatabaseObjects.DatabaseNode.Language import Language
from src.DatabaseObjects.DatabaseNode.Topic import Topic
from src.DatabaseObjects.DatabaseNode.Organization import Organization
from src.DatabaseObjects.DatabaseRelationship.User import UserOwnsProject
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectIsLicensed, ProjectHasTopic, \
    ProjectContainsLanguage
from src.DatabaseObjects.DatabaseRelationship.Organization import OrganizationOwnsProject


class ProjectProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        project_data = self.get_data().get("repository", None)
        # Construct project node
        project_node = Project().extract_and_update(project_data)
        self.get_repo().set_project_id(project_data["id"])
        self.get_repo().get_preprocessor_storage().add_node(project_node)
        self.set_node(project_node)

        # Project License processor
        license_data = project_data.get("licenseInfo", None)
        if license_data is not None:
            license_processor = LicenseProcessor(self.get_repo(), license_data, self)
            license_processor.process()

        # Project owner processor
        owner_data = project_data.get("owner", None)
        if owner_data is None:
            owner_data = User.get_default_user_data()
        project_owner_processor = ProjectOwnerProcessor(self.get_repo(), owner_data, self)
        project_owner_processor.process()

        # Project topic processor
        topics_data = project_data.get("repositoryTopics", None)
        for topic_data in topics_data.get("nodes", []):
            # Edge case
            if topic_data is None:
                continue
            topic_processor = TopicProcessor(self.get_repo(), topic_data, self)
            topic_processor.process()

        # Project languages processor
        languages_data = project_data.get("languages", None)
        for language_data in languages_data.get("nodes", []):
            # Edge case
            if language_data is None:
                continue
            language_processor = LanguageProcessorProcessor(self.get_repo(), language_data, self)
            language_processor.process()


class TopicProcessor(ProcessorTemplate):

    def process(self):
        # Construct Topic node
        topic_node = Topic().extract_and_update(self.get_data()["topic"])
        self.get_repo().get_preprocessor_storage().add_node(topic_node)

        # Construct project -[HAS_TOPIC]-> Relationship
        project_has_topic_relationship = ProjectHasTopic().set_source_node(
            self.get_parent().get_node()
        ).set_destination_node(topic_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_has_topic_relationship)


class LanguageProcessorProcessor(ProcessorTemplate):

    def process(self):
        # Construct Language node
        language_name = self.get_data().get("name", None)
        if language_name is None:
            return
        language_node = Language().extract_and_update({"name": language_name})
        self.get_repo().get_preprocessor_storage().add_node(language_node)

        # Construct project -[PROJECT_CONTAINS_LANGUAGE]-> Language
        project_contains_language_relationship = ProjectContainsLanguage()
        project_contains_language_relationship.set_source_node(self.get_parent().get_node())
        project_contains_language_relationship.set_destination_node(language_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_contains_language_relationship)


class LicenseProcessor(ProcessorTemplate):

    def process(self):
        # Construct License node
        license_node = License().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(license_node)

        # Construct project -[IS_LICENSED]-> Relationship
        project_is_licensed_relationship = ProjectIsLicensed().set_source_node(
            self.get_parent().get_node()
        ).set_destination_node(license_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_is_licensed_relationship)


class ProjectOwnerProcessor(ProcessorTemplate):

    def process(self):
        if "id" in self.get_data().keys():
            # Construct owner node
            owner_node = User().extract_and_update(self.get_data())
            self.get_repo().get_preprocessor_storage().add_node(owner_node)

            # Construct user -[OWNS]-> project relationship
            user_owns_project_relationship = UserOwnsProject().set_source_node(owner_node).set_destination_node(
                self.get_parent().get_node()
            )
            user_owns_project_relationship.extract_and_update(self.get_data())
            self.get_repo().get_preprocessor_storage().add_relationship(user_owns_project_relationship)
        if "orgId" in self.get_data().keys():
            # Construct organization node
            organization_node = Organization().extract_and_update(self.get_data())
            self.get_repo().get_preprocessor_storage().add_node(organization_node)

            # Construct organization -[OWNS]-> project relationship
            org_owns_project_relationship = OrganizationOwnsProject().set_source_node(
                organization_node
            ).set_destination_node(
                self.get_parent().get_node()
            )
            org_owns_project_relationship.extract_and_update(self.get_data())
            self.get_repo().get_preprocessor_storage().add_relationship(org_owns_project_relationship)
