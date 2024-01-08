from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot, ProcessorTemplate
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseRelationship.User import WatchesProject


class WatchesProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        for watcher in self.get_data().get("nodes", None):
            if watcher is None:
                continue
            single_watcher = WatcherProcessor(self.get_repo(), watcher, self)
            single_watcher.process()


class WatcherProcessor(ProcessorTemplate):
    def process(self):
        # Construct User node
        watcher_node = User().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(watcher_node)
        # Construct project node
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        # Construct user -[WATCHES]-> project relationship
        user_watches_project_relationship = WatchesProject()
        user_watches_project_relationship.set_source_node(watcher_node)
        user_watches_project_relationship.set_destination_node(project_node)
        self.get_repo().get_preprocessor_storage().add_relationship(user_watches_project_relationship)
