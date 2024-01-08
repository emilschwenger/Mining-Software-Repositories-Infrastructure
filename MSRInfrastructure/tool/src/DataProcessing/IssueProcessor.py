from datetime import datetime
from src.DataProcessing.ProcessorTemplate import ProcessorTemplate, ProcessorTemplateRoot
from src.DatabaseObjects.DatabaseNode.Issue import Issue, ProjectIssueMonth
from src.DatabaseObjects.DatabaseNode.Milestone import Milestone
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseNode.Label import Label
from src.DatabaseObjects.DatabaseRelationship.User import CreatesMilestone, ClosesIssue, CreatesIssue, \
    GetsAssignedIssue, CommentsOnIssue
from src.DatabaseObjects.DatabaseRelationship.Issue import IssueInMonth, IssueHasLabel
from src.DatabaseObjects.DatabaseRelationship.Milestone import RequiresIssue
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasIssueMonth
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasMilestone


class IssueProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        for issue in self.get_data()["nodes"]:
            single_issue = IssueProcessor(self.get_repo(), issue, self)
            single_issue.process()


class IssueProcessor(ProcessorTemplate):

    def process(self):
        # Create the current issue node
        issue_node = Issue().extract_and_update(self.get_data())
        self.set_node(issue_node)

        # Construct Issue time aggregator node
        issue_creation_time_string = self.get_data().get("createdAt")
        issue_creation_time_datetime = datetime.strptime(issue_creation_time_string, "%Y-%m-%dT%H:%M:%SZ")
        issue_time_aggregator_node_id = self.get_repo().get_preprocessor_storage().get_issue_time_aggregator_id(
            time=issue_creation_time_string
        )
        project_issue_month_node = ProjectIssueMonth().extract_and_update({
            "id": issue_time_aggregator_node_id,
            "year": issue_creation_time_datetime.year,
            "month": issue_creation_time_datetime.month
        })
        self.get_repo().get_preprocessor_storage().add_node(project_issue_month_node)

        # Construct relationship Issue -[ISSUE_IN_MONTH]-> ProjectIssueMonth
        issue_in_month_relationship = IssueInMonth()
        issue_in_month_relationship.set_source_node(issue_node)
        issue_in_month_relationship.set_destination_node(project_issue_month_node)
        self.get_repo().get_preprocessor_storage().add_relationship(issue_in_month_relationship)

        # Construct Project -[HAS_ISSUE_MONTH]-> IssueMonth
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        project_issue_month_relationship = ProjectHasIssueMonth()
        project_issue_month_relationship.set_source_node(project_node)
        project_issue_month_relationship.set_destination_node(project_issue_month_node)
        project_issue_month_relationship.extract_and_update({
            "date_month": datetime(issue_creation_time_datetime.year, issue_creation_time_datetime.month, 1).strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        self.get_repo().get_preprocessor_storage().add_relationship(project_issue_month_relationship)

        # Step 1: Process milestone connected to issue
        if self.get_data()["milestone"] is not None:
            milestone_data = self.get_data()["milestone"]
            issue_milestone_processor = IssueMilestoneProcessor(self.get_repo(), milestone_data, self)
            issue_milestone_processor.process()

        # Step 2: Process timeline data
        timeline_data = self.get_data()["timelineItems"]
        for timeline_item in timeline_data["nodes"]:
            if timeline_item is None:
                continue
            issue_timeline_processor = IssueTimelineProcessor(self.get_repo(), timeline_item, self)
            issue_timeline_processor.process()

        # Step 3: Process author connected to issue
        author_data = self.get_data()["author"]
        if author_data is None:
            author_data = User.get_default_user_data()
        issue_author_processor = IssueAuthorProcessor(self.get_repo(), author_data, self)
        issue_author_processor.process()

        # Step 4: Process assignees data
        assignees_data = self.get_data()["assignees"]
        for assignee_item in assignees_data["nodes"]:
            if assignee_item is None:
                continue
            assignee_processor = IssueAssigneeProcessor(self.get_repo(), assignee_item, self)
            assignee_processor.process()

        # Step 5: Process label data
        label_data = self.get_data()["labels"]
        for label_item in label_data["nodes"]:
            if label_item is None:
                continue
            label_processor = IssueLabelProcessor(self.get_repo(), label_item, self)
            label_processor.process()

        # Step 6: Process comments data
        comment_data = self.get_data()["comments"]
        for comment_item in comment_data["nodes"]:
            if comment_item is None:
                continue
            comment_processor = IssueCommentProcessor(self.get_repo(), comment_item, self)
            comment_processor.process()

        # Write issue node --> In the end to set convertedToDiscussion
        self.get_repo().get_preprocessor_storage().add_node(issue_node)



class IssueMilestoneProcessor(ProcessorTemplate):
    def process(self):
        # Construct milestone node
        milestone_node = Milestone().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(milestone_node)
        self.set_node(milestone_node)

        # Construct milestone creator node
        milestone_creator_data = self.get_data()["creator"]
        if milestone_creator_data is None:
            milestone_creator_data = User.get_default_user_data()
        milestone_creator_node = User().extract_and_update(milestone_creator_data)
        self.get_repo().get_preprocessor_storage().add_node(milestone_creator_node)

        # Construct user -[CREATES_MILESTONE]-> milestone relationship
        creates_milestone_relationship = CreatesMilestone().set_source_node(
            milestone_creator_node).set_destination_node(milestone_node)
        creates_milestone_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(creates_milestone_relationship)

        # Construct Project -[HAS_MILESTONE]-> Milestone
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        project_milestone_relationship = ProjectHasMilestone()
        project_milestone_relationship.set_source_node(project_node)
        project_milestone_relationship.set_destination_node(milestone_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_milestone_relationship)

        # Construct milestone -[REQUIRES]-> issue relationship
        requires_issue_relationship = RequiresIssue().set_source_node(milestone_node).set_destination_node(
            self.get_parent().get_node()
        )
        self.get_repo().get_preprocessor_storage().add_relationship(requires_issue_relationship)


class IssueTimelineProcessor(ProcessorTemplate):
    """
    Collects: CLOSED EVENT
    """

    def process(self):
        if self.get_data()["__typename"] == "ClosedEvent":
            actor_data = self.get_data()["actor"]
            # Edge case that actor is deleted
            if actor_data is None:
                actor_data = User.get_default_user_data()
            # Construct event actor node
            milestone_creator_node = User().extract_and_update(actor_data)
            self.get_repo().get_preprocessor_storage().add_node(milestone_creator_node)

            # Construct user -[CLOSES_ISSUE]-> issue
            user_closes_issue_relationship = ClosesIssue().set_source_node(milestone_creator_node).set_destination_node(
                self.get_parent().get_node()
            )
            user_closes_issue_relationship.extract_and_update(self.get_data())
            self.get_repo().get_preprocessor_storage().add_relationship(user_closes_issue_relationship)
        if self.get_data()["__typename"] == "ConvertedToDiscussionEvent":
            # Update issue node
            self.get_parent().get_node().extract_and_update({
                "convertedToDiscussion": True
            })
        # TODO: Add more timeline event handling


class IssueAuthorProcessor(ProcessorTemplate):

    def process(self):
        # Construct issue author node
        issue_author_node = User().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(issue_author_node)

        # Construct user -[CREATES]-> Issue
        author_issue_relationship = CreatesIssue().set_source_node(issue_author_node).set_destination_node(
            self.get_parent().get_node()
        )
        author_issue_relationship.extract_and_update(self.get_parent().get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_issue_relationship)


class IssueLabelProcessor(ProcessorTemplate):

    def process(self):
        # Construct label node
        issue_label_node = Label().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(issue_label_node)

        # Construct issue -[ISSUE_HAS_LABEL]-> label
        issue_has_label_relationship = IssueHasLabel().set_source_node(
            self.get_parent().get_node()).set_destination_node(
            issue_label_node
        )
        self.get_repo().get_preprocessor_storage().add_relationship(issue_has_label_relationship)


class IssueAssigneeProcessor(ProcessorTemplate):

    def process(self):
        # Construct assignee node
        issue_assignee_node = User().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(issue_assignee_node)

        # Construct user -[GETS_ASSIGNED_ISSUE]-> issue
        assignee_issue_relationship = GetsAssignedIssue().set_source_node(issue_assignee_node).set_destination_node(
            self.get_parent().get_node()
        )
        self.get_repo().get_preprocessor_storage().add_relationship(assignee_issue_relationship)


class IssueCommentProcessor(ProcessorTemplate):

    def process(self):
        comment_author_data = self.get_data()["author"]

        # Edge case if author is deleted
        if comment_author_data is None:
            comment_author_data = User.get_default_user_data()

        # Construct comment author node
        comment_author_node = User().extract_and_update(comment_author_data)
        self.get_repo().get_preprocessor_storage().add_node(comment_author_node)

        # Construct user -[COMMENTS_ON_ISSUE]-> issue
        user_comments_issue_relationship = CommentsOnIssue().set_source_node(comment_author_node).set_destination_node(
            self.get_parent().get_node()
        )
        user_comments_issue_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(user_comments_issue_relationship)
