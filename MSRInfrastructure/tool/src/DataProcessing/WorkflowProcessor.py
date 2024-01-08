from src.DataProcessing.ProcessorTemplate import ProcessorTemplateRoot, ProcessorTemplate
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseNode.Commit import Commit
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.Workflow import WorkflowRun, Workflow
from src.DatabaseObjects.DatabaseRelationship.User import CreatesWorkflowRun, TriggersWorkflowRun
from src.DatabaseObjects.DatabaseRelationship.Workflow import HasWorkflowRun
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasWorkflow
from src.DatabaseObjects.DatabaseRelationship.WorkflowRun import WorkflowRunHasHeadCommit

class WorkflowProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        # Construct workflow node
        workflow_node = Workflow().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(workflow_node)
        self.set_node(workflow_node)

        # Construct Project -[HAS_WORKFLOW]-> Workflow
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        project_workflow_relationship = ProjectHasWorkflow()
        project_workflow_relationship.set_source_node(project_node)
        project_workflow_relationship.set_destination_node(workflow_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_workflow_relationship)

        workflow_runs = self.get_data().get("workflowRuns", [])
        for workflow_run in workflow_runs:
            workflow_run_processor = WorkflowRunProcessor(self.get_repo(), workflow_run, self)
            workflow_run_processor.process()


class WorkflowRunProcessor(ProcessorTemplate):

    def process(self):
        # Construct workflow run node
        workflow_run_node = WorkflowRun().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(workflow_run_node)

        # Process workflow head commit and workflow
        head_commit_hash = self.get_data().get("headCommit", None)
        if head_commit_hash is not None and len(head_commit_hash) > 0:
            # Construct commit node
            head_commit_node = Commit().extract_and_update({"hash": head_commit_hash})
            # Construct relationship WorkflowRun -[:WORKFLOW_RUN_HAS_HEAD_COMMIT]-> Commit
            workflow_run_head_commit_relationship = WorkflowRunHasHeadCommit()
            workflow_run_head_commit_relationship.set_source_node(workflow_run_node)
            workflow_run_head_commit_relationship.set_destination_node(head_commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(workflow_run_head_commit_relationship)

        # Construct actor node
        actor_data = self.get_data().get("actor", None)
        if actor_data is None:
            actor_data = User.get_default_user_data()
        actor_node = User().extract_and_update(actor_data)
        self.get_repo().get_preprocessor_storage().add_node(actor_node)

        # Construct User -[CREATES_WORKFLOW_RUN]-> WorkflowRun
        workflow_run_actor_relationship = CreatesWorkflowRun()
        workflow_run_actor_relationship.extract_and_update(self.get_data())
        workflow_run_actor_relationship.set_source_node(actor_node)
        workflow_run_actor_relationship.set_destination_node(workflow_run_node)
        self.get_repo().get_preprocessor_storage().add_relationship(workflow_run_actor_relationship)

        # Construct actor node
        triggering_actor_data = self.get_data().get("triggeringActor", None)
        if triggering_actor_data is None:
            triggering_actor_data = User.get_default_user_data()
        triggering_actor_node = User().extract_and_update(triggering_actor_data)
        self.get_repo().get_preprocessor_storage().add_node(triggering_actor_node)

        # Construct User -[TRIGGERS_WORKFLOW_RUN]-> WorkflowRun
        workflow_run_triggering_actor_relationship = TriggersWorkflowRun()
        workflow_run_triggering_actor_relationship.extract_and_update(self.get_data())
        workflow_run_triggering_actor_relationship.set_source_node(triggering_actor_node)
        workflow_run_triggering_actor_relationship.set_destination_node(workflow_run_node)
        self.get_repo().get_preprocessor_storage().add_relationship(workflow_run_triggering_actor_relationship)

        # Construct Workflow -[HAS_WORKFLOW_RUN]-> WorkflowRun
        workflow_has_run_relationship = HasWorkflowRun()
        workflow_has_run_relationship.set_source_node(self.get_parent().get_node())
        workflow_has_run_relationship.set_destination_node(workflow_run_node)
        self.get_repo().get_preprocessor_storage().add_relationship(workflow_has_run_relationship)
