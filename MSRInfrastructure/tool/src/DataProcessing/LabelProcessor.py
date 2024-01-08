from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot, ProcessorTemplate
from src.DatabaseObjects.DatabaseNode.Label import Label
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasLabel


class LabelProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        for labels in self.get_data().get("nodes", None):
            if labels is None:
                continue
            single_label = LabelProcessor(self.get_repo(), labels, self)
            single_label.process()


class LabelProcessor(ProcessorTemplate):
    def process(self):
        # Construct Label node
        label_node = Label().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(label_node)

        # Construct Project -[HAS_LABEL]-> Label
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        project_label_relationship = ProjectHasLabel()
        project_label_relationship.set_source_node(project_node)
        project_label_relationship.set_destination_node(label_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_label_relationship)
