from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot, ProcessorTemplate
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.Dependency import Dependency
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectIsDependentOn


class DependencyProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        for dependency in self.get_data():
            if dependency is None:
                continue
            single_dependency = DependencyProcessor(self.get_repo(), dependency, self)
            single_dependency.process()


class DependencyProcessor(ProcessorTemplate):
    def process(self):
        # Construct dependency node
        dependency_node = Dependency().extract_and_update(self.get_data())
        dependency_node.extract_and_update({
            "nameAndVersion": self.get_data().get("name", "") + "-" + self.get_data().get("versionInfo", "")
        })
        self.get_repo().get_preprocessor_storage().add_node(dependency_node)
        # Construct project node
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        # Construct Project -[DEPENDS_ON]-> Dependency relationship
        project_dependent_on_relationship = ProjectIsDependentOn()
        project_dependent_on_relationship.set_source_node(project_node)
        project_dependent_on_relationship.set_destination_node(dependency_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_dependent_on_relationship)
