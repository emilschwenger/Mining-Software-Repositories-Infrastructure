from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot, ProcessorTemplate
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseRelationship.User import StarsProject


class StarsProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        for stargazer in self.get_data().get("nodes", None):
            if stargazer is None:
                continue
            single_stargazer = StargazerProcessor(self.get_repo(), stargazer, self)
            single_stargazer.process()


class StargazerProcessor(ProcessorTemplate):
    def process(self):
        # Construct User node
        stargazer_node = User().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(stargazer_node)
        # Construct project node
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        # Construct user -[STARS]-> project relationship
        user_stars_project_relationship = StarsProject()
        user_stars_project_relationship.set_source_node(stargazer_node)
        user_stars_project_relationship.set_destination_node(project_node)
        self.get_repo().get_preprocessor_storage().add_relationship(user_stars_project_relationship)
