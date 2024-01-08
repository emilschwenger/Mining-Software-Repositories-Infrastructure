from datetime import datetime
from src.DataProcessing.ProcessorTemplate import ProcessorTemplate, ProcessorTemplateRoot
from src.DatabaseObjects.DatabaseNode.Milestone import Milestone
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseNode.Commit import Commit
from src.DatabaseObjects.DatabaseNode.Branch import Branch
from src.DatabaseObjects.DatabaseNode.PullRequest import PullRequest, ProjectPullRequestMonth, PullRequestEvent, \
    PullRequestReviewComment, PullRequestReview, PullRequestFile
from src.DatabaseObjects.DatabaseNode.Label import Label
from src.DatabaseObjects.DatabaseRelationship.User import CreatesMilestone, CommentsOnPullRequest, \
    GetsAssignedPullRequest, CreatesPullRequest, CreatesPullRequestEvent, CreatesPullRequestReview, \
    CreatesPullRequestReviewComment
from src.DatabaseObjects.DatabaseRelationship.PullRequest import PullRequestInMonth, PullRequestHasLabel, \
    RequestsReviewer, PullRequestHasEvent, PullRequestEventLinksCommit, IsReplyToPullRequestReviewComment, \
    IsPullRequestBaseCommit, CommentsOnPullRequestReview, PullRequestHasReview, PullRequestProposesFileChange, \
    IsSinglePullRequestReviewComment, IsPullRequestHeadCommit, PullRequestReviewReviewsCommit, \
    PullRequestReviewCommentCommentsCommit, PullRequestReviewCommentCommentsOriginalCommit, \
    PullRequestHasSourceBranch, PullRequestHasTargetBranch
from src.DatabaseObjects.DatabaseRelationship.Milestone import RequiresPullRequest
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasPullRequestMonth
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasMilestone
from src.Utility.Utility import dict_search

class PullRequestProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        for pull_request in self.get_data().get("nodes", []):
            single_pull_request = PullRequestProcessor(self.get_repo(), pull_request, self)
            single_pull_request.process()


class PullRequestProcessor(ProcessorTemplate):

    def process(self):
        # Construct pull request node
        pull_request_node = PullRequest().extract_and_update(self.get_data())

        # Get base and head repository url
        pull_request_node.extract_and_update({
            "baseRepositoryURL": dict_search(self.get_data(), ["baseRepository", "url"], ""),
            "headRepositoryURL": dict_search(self.get_data(), ["headRepository", "url"], ""),
        })
        self.get_repo().get_preprocessor_storage().add_node(pull_request_node)
        self.set_node(pull_request_node)

        # Construct pull request time aggregator node
        pull_request_creation_time_string = self.get_data().get("createdAt")
        pull_request_creation_time_datetime = datetime.strptime(pull_request_creation_time_string, "%Y-%m-%dT%H:%M:%SZ")
        pull_request_time_aggregator_node_id = self.get_repo().get_preprocessor_storage().get_pull_request_time_aggregator_id(
            time=pull_request_creation_time_string
        )
        project_pull_request_month_node = ProjectPullRequestMonth().extract_and_update({
            "id": pull_request_time_aggregator_node_id,
            "year": pull_request_creation_time_datetime.year,
            "month": pull_request_creation_time_datetime.month
        })
        self.get_repo().get_preprocessor_storage().add_node(project_pull_request_month_node)

        # Construct relationship PullRequest -[PULL_REQUEST_IN_MONTH]-> ProjectPullRequestMonth
        pull_request_in_month_relationship = PullRequestInMonth().set_source_node(
            pull_request_node).set_destination_node(
            project_pull_request_month_node
        )
        self.get_repo().get_preprocessor_storage().add_relationship(pull_request_in_month_relationship)

        # Construct Project -[HAS_PULL_REQUEST_MONTH]-> PullRequestMonth
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })
        project_pull_request_month_relationship = ProjectHasPullRequestMonth()
        project_pull_request_month_relationship.set_source_node(project_node)
        project_pull_request_month_relationship.set_destination_node(project_pull_request_month_node)
        project_pull_request_month_relationship.extract_and_update({
            "date_month": datetime(
                pull_request_creation_time_datetime.year,
                pull_request_creation_time_datetime.month,
                1).strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        self.get_repo().get_preprocessor_storage().add_relationship(project_pull_request_month_relationship)

        # Construct HEAD and BASE Branch nodes
        head_repository_id = dict_search(self.get_data(), ["headRepository", "id"], None)
        base_repository_id = dict_search(self.get_data(), ["baseRepository", "id"], None)
        head_ref_name = dict_search(self.get_data(), ["headRefName"], None)
        base_ref_name = dict_search(self.get_data(), ["baseRefName"], None)
        if base_repository_id is not None and base_ref_name is not None:
            base_branch_node = Branch().extract_and_update({
                "id": self.get_repo().get_preprocessor_storage().get_branch_id(
                    base_repository_id,
                    "origin/" + base_ref_name)
            })
            # Construct PullRequest -[:PULL_:REQUEST_HAS_TARGET_BRANCH]-> Branch
            pull_request_target_branch_relationship = PullRequestHasTargetBranch()
            pull_request_target_branch_relationship.set_source_node(pull_request_node)
            pull_request_target_branch_relationship.set_destination_node(base_branch_node)
            self.get_repo().get_preprocessor_storage().add_relationship(pull_request_target_branch_relationship)
        if head_repository_id is not None and head_ref_name is not None and base_repository_id == head_repository_id:
            head_branch_node = Branch().extract_and_update({
                "id": self.get_repo().get_preprocessor_storage().get_branch_id(
                    head_repository_id,
                    "origin/" + head_ref_name)
            })
            # Construct PullRequest -[:PULL_:REQUEST_HAS_SOURCE_BRANCH]-> Branch
            pull_request_source_branch_relationship = PullRequestHasSourceBranch()
            pull_request_source_branch_relationship.set_source_node(pull_request_node)
            pull_request_source_branch_relationship.set_destination_node(head_branch_node)
            self.get_repo().get_preprocessor_storage().add_relationship(pull_request_source_branch_relationship)

        # Construct base commit node and relationship
        base_commit_hash = self.get_data().get("baseRefOid", None)
        if base_commit_hash is not None:
            # Construct base commit node
            base_commit_node = Commit().extract_and_update({"hash": base_commit_hash})
            # Construct relationship PullRequest -[IS_PULL_REQUEST_BASE_COMMIT]-> Commit
            pull_request_base_commit_relationship = IsPullRequestBaseCommit()
            pull_request_base_commit_relationship.set_source_node(pull_request_node)
            pull_request_base_commit_relationship.set_destination_node(base_commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(pull_request_base_commit_relationship)

        # Construct base commit node and relationship
        head_commit_hash = self.get_data().get("headRefOid", None)
        if head_commit_hash is not None:
            # Construct head commit node
            head_commit_node = Commit().extract_and_update({"hash": head_commit_hash})
            # Construct relationship PullRequest -[IS_PULL_REQUEST_HEAD_COMMIT]-> Commit
            pull_request_head_commit_relationship = IsPullRequestHeadCommit()
            pull_request_head_commit_relationship.set_source_node(pull_request_node)
            pull_request_head_commit_relationship.set_destination_node(head_commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(pull_request_head_commit_relationship)

        # Process author
        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        author_processor = PullRequestAuthorProcessor(self.get_repo(), author_data, self)
        author_processor.process()

        # Process milestone connected to pull request
        if self.get_data().get("milestone", None) is not None:
            milestone_data = self.get_data()["milestone"]
            milestone_processor = PullRequestMilestoneProcessor(self.get_repo(), milestone_data, self)
            milestone_processor.process()

        # Process requested reviewers
        requested_reviewers_data = self.get_data().get("reviewRequests", None)
        for requested_reviewer_data in requested_reviewers_data.get("nodes", []):
            if requested_reviewer_data is None:
                continue
            requested_reviewer_processor = RequestedReviewerProcessor(self.get_repo(), requested_reviewer_data, self)
            requested_reviewer_processor.process()

        # Assignees processor
        assignees_data = self.get_data().get("assignees", None)
        for assignee_data in assignees_data.get("nodes", []):
            if assignee_data is None:
                continue
            assignee_processor = PullRequestAssigneeProcessor(self.get_repo(), assignee_data, self)
            assignee_processor.process()

        # Assignees processor
        labels_data = self.get_data().get("labels", None)
        for label_data in labels_data.get("nodes", []):
            if label_data is None:
                continue
            label_processor = PullRequestLabelProcessor(self.get_repo(), label_data, self)
            label_processor.process()

        # If pull request file content is not needed, we collect data with GraphQL. If content is needed, we retrieve
        # data later with the REST API
        if not self.get_repo().isCollectPullRequestFileContent():
            # Files processor
            files_data = self.get_data().get("files", None)
            for file_data in files_data.get("nodes", []):
                if file_data is None:
                    continue
                file_processor = PullRequestFileProcessor(self.get_repo(), file_data, self)
                file_processor.process()

        # Pull request comment processor
        comments_data = self.get_data().get("comments", None)
        for comment_data in comments_data.get("nodes", []):
            if comment_data is None:
                continue
            comment_processor = PullRequestCommentProcessor(self.get_repo(), comment_data, self)
            comment_processor.process()

        # Pull request timeline processor
        timeline_data = self.get_data().get("timelineItems", None)
        for event_data in timeline_data.get("nodes", []):
            if event_data is None:
                continue
            event_processor = PullRequestTimelineProcessor(self.get_repo(), event_data, self)
            event_processor.process()

        # Pull request review processor
        reviews_data = self.get_data().get("reviews", None)
        for review_data in reviews_data.get("nodes", []):
            if review_data is None:
                continue
            review_processor = PullRequestReviewProcessor(self.get_repo(), review_data, self)
            review_processor.process()


class PullRequestMilestoneProcessor(ProcessorTemplate):
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
            milestone_creator_node
        ).set_destination_node(milestone_node)
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

        # Construct milestone -[REQUIRES]-> PullRequest relationship
        requires_pull_request_relationship = RequiresPullRequest().set_source_node(milestone_node).set_destination_node(
            self.get_parent().get_node()
        )
        self.get_repo().get_preprocessor_storage().add_relationship(requires_pull_request_relationship)


class PullRequestAuthorProcessor(ProcessorTemplate):

    def process(self):
        # Construct pull request author node
        pull_request_author_node = User().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(pull_request_author_node)
        # Construct Relationship user-[CREATES]-> PullRequest
        pull_request_author_relationship = CreatesPullRequest().set_source_node(
            pull_request_author_node).set_destination_node(
            self.get_parent().get_node()
        )
        pull_request_author_relationship.extract_and_update(self.get_parent().get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(pull_request_author_relationship)


class RequestedReviewerProcessor(ProcessorTemplate):

    def process(self):
        reviewer_data = self.get_data().get("requestedReviewer", None)
        if reviewer_data is None:
            reviewer_data = User.get_default_user_data()
        # Construct requested reviewer node
        reviewer_node = User().extract_and_update(reviewer_data)
        self.get_repo().get_preprocessor_storage().add_node(reviewer_node)

        # Construct Relationship PullRequest -[REQUESTS_REVIEWER]-> User
        pull_request_reviewer_relationship = RequestsReviewer()
        pull_request_reviewer_relationship.set_source_node(self.get_parent().get_node())
        pull_request_reviewer_relationship.set_destination_node(reviewer_node)
        self.get_repo().get_preprocessor_storage().add_relationship(pull_request_reviewer_relationship)


class PullRequestAssigneeProcessor(ProcessorTemplate):

    def process(self):
        # Construct assignee node
        pull_request_assignee_node = User().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(pull_request_assignee_node)

        # Construct user -[GETS_ASSIGNED_PULL_REQUEST]-> PullRequest
        assignee_pull_request_relationship = GetsAssignedPullRequest()
        assignee_pull_request_relationship.set_source_node(pull_request_assignee_node)
        assignee_pull_request_relationship.set_destination_node(self.get_parent().get_node())
        self.get_repo().get_preprocessor_storage().add_relationship(assignee_pull_request_relationship)


class PullRequestLabelProcessor(ProcessorTemplate):

    def process(self):
        # Construct label node
        pull_request_label_node = Label().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(pull_request_label_node)

        # Construct PullRequest -[PULL_REQUEST_HAS_LABEL]-> label
        pull_request_has_label_relationship = PullRequestHasLabel()
        pull_request_has_label_relationship.set_source_node(self.get_parent().get_node())
        pull_request_has_label_relationship.set_destination_node(pull_request_label_node)
        self.get_repo().get_preprocessor_storage().add_relationship(pull_request_has_label_relationship)


class PullRequestCommentProcessor(ProcessorTemplate):

    def process(self):
        comment_author_data = self.get_data().get("author", None)
        if comment_author_data is None:
            comment_author_data = User.get_default_user_data()
        # Construct comment author node
        comment_author_node = User().extract_and_update(comment_author_data)
        self.get_repo().get_preprocessor_storage().add_node(comment_author_node)
        # Construct User -[COMMENTS_ON_PULL_REQUEST]-> PullRequest
        author_comment_relationship = CommentsOnPullRequest()
        author_comment_relationship.set_source_node(comment_author_node)
        author_comment_relationship.set_destination_node(self.get_parent().get_node())
        author_comment_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_comment_relationship)


class PullRequestTimelineProcessor(ProcessorTemplate):

    def process(self):
        # Construct actor node if key exists
        actor_node = None
        actor_data = self.get_data().get("actor", None)
        if actor_data is None:
            actor_data = User.get_default_user_data()
        actor_node = User().extract_and_update(actor_data)
        self.get_repo().get_preprocessor_storage().add_node(actor_node)
        # Process event types
        event_node = None
        event_typename = self.get_data().get("__typename", None)
        if event_typename is None:
            return
        if event_typename == "MergedEvent":
            # Construct PullRequestEvent node
            event_node = PullRequestEvent().extract_and_update(self.get_data())
            self.get_repo().get_preprocessor_storage().add_node(event_node)
            # Check event commit data
            commit_data = self.get_data().get("commit", None)
            if commit_data is not None and "oid" in commit_data:
                # Construct commit node
                commit_hash = commit_data.get("oid")
                event_commit_node = Commit().extract_and_update({"hash": commit_hash})
                # Construct PullRequestEvent -[PULL_REQUEST_EVENT_LINKS_COMMIT]-> Commit relationship
                event_links_commit_relationship = PullRequestEventLinksCommit()
                event_links_commit_relationship.set_source_node(event_node)
                event_links_commit_relationship.set_destination_node(event_commit_node)
                self.get_repo().get_preprocessor_storage().add_relationship(event_links_commit_relationship)
        if event_typename == "ClosedEvent":
            # Construct PullRequestEvent node
            event_node = PullRequestEvent().extract_and_update(self.get_data())
            self.get_repo().get_preprocessor_storage().add_node(event_node)
        if actor_node is not None and event_node is not None:
            # Construct User -[CREATES_PULL_REQUEST_EVENT]-> PullRequest
            user_creates_event_relationship = CreatesPullRequestEvent()
            user_creates_event_relationship.set_source_node(actor_node)
            user_creates_event_relationship.set_destination_node(event_node)
            user_creates_event_relationship.extract_and_update(self.get_data())
            self.get_repo().get_preprocessor_storage().add_relationship(user_creates_event_relationship)
        if event_node is not None:
            # Construct PullRequest -[PULL_REQUEST_HAS_EVENT]-> PullRequestEvent
            pull_request_has_event_relationship = PullRequestHasEvent()
            pull_request_has_event_relationship.set_source_node(self.get_parent().get_node())
            pull_request_has_event_relationship.set_destination_node(event_node)
            self.get_repo().get_preprocessor_storage().add_relationship(pull_request_has_event_relationship)


class PullRequestReviewProcessor(ProcessorTemplate):

    def process(self):
        # Construct pull request review node
        review_node = PullRequestReview().extract_and_update(self.get_data())
        # Update pull request review node commit hash if existent
        review_commit_hash = dict_search(self.get_data(), ["commit", "oid"], None)
        if review_commit_hash is not None:
            review_node.extract_and_update({"commitHash": review_commit_hash})
        self.get_repo().get_preprocessor_storage().add_node(review_node)
        self.set_node(review_node)

        if review_commit_hash is not None:
            # Construct commit node
            review_commit_node = Commit().extract_and_update({"hash": review_commit_hash})
            # Construct PullRequestReview -[:REVIEWS_COMMIT]-> Commit
            review_commit_relationship = PullRequestReviewReviewsCommit()
            review_commit_relationship.set_source_node(review_node)
            review_commit_relationship.set_destination_node(review_commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(review_commit_relationship)

        # Construct author node
        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)

        # Construct user -[CREATES_PULL_REQUEST_REVIEW]-> PullRequest relationship
        creates_pull_request_review_relationship = CreatesPullRequestReview()
        creates_pull_request_review_relationship.set_source_node(author_node)
        creates_pull_request_review_relationship.set_destination_node(review_node)
        creates_pull_request_review_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(creates_pull_request_review_relationship)

        # Construct PullRequest -[PULL_REQUEST_HAS_REVIEW]- PullRequestReview relationship
        pull_request_has_review_relationship = PullRequestHasReview()
        pull_request_has_review_relationship.set_source_node(self.get_parent().get_node())
        pull_request_has_review_relationship.set_destination_node(review_node)
        self.get_repo().get_preprocessor_storage().add_relationship(pull_request_has_review_relationship)

        # Start processing pull request review comments
        pull_request_review_comments_data = self.get_data().get("comments", None)
        for pull_request_review_comment_data in pull_request_review_comments_data.get("nodes", []):
            if pull_request_review_comment_data is None:
                continue
            comment_processor = PullRequestReviewCommentProcessor(self.get_repo(), pull_request_review_comment_data, self)
            comment_processor.process()


class PullRequestReviewCommentProcessor(ProcessorTemplate):

    def process(self):
        # Construct pull request review comment node
        comment_node = PullRequestReviewComment().extract_and_update(self.get_data())
        # Update commit and original commit data in review node
        comment_commit_hash = dict_search(self.get_data(), ["commit", "oid"], None)
        if comment_commit_hash is not None:
            comment_node.extract_and_update({"commitHash": comment_commit_hash})
        comment_original_commit_hash = dict_search(self.get_data(), ["originalCommit", "oid"], None)
        if comment_original_commit_hash is not None:
            comment_node.extract_and_update({"originalCommitHash": comment_original_commit_hash})
        self.get_repo().get_preprocessor_storage().add_node(comment_node)

        # Process comment commit
        if comment_commit_hash is not None:
            comment_commit_node = Commit().extract_and_update({"hash": comment_commit_hash})
            # Construct PullRequestReviewComment -[:PULL_REQUEST_REVIEW_COMMENT_COMMENTS_COMMIT]-> Commit
            comment_commit_relationship = PullRequestReviewCommentCommentsCommit()
            comment_commit_relationship.set_source_node(comment_node)
            comment_commit_relationship.set_destination_node(comment_commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(comment_commit_relationship)

        # Process comment original commit
        if comment_original_commit_hash is not None:
            comment_original_commit_node = Commit().extract_and_update({"hash": comment_original_commit_hash})
            # Construct PullRequestReviewComment -[:PULL_REQUEST_REVIEW_COMMENT_COMMENTS_ORIGINAL_COMMIT]-> Commit
            comment_commit_relationship = PullRequestReviewCommentCommentsOriginalCommit()
            comment_commit_relationship.set_source_node(comment_node)
            comment_commit_relationship.set_destination_node(comment_original_commit_node)
            self.get_repo().get_preprocessor_storage().add_relationship(comment_commit_relationship)

        # Construct author node
        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)

        # Construct user -[CREATES_COMMENT]-> PullRequestReviewComment
        author_creates_comment_relationship = CreatesPullRequestReviewComment()
        author_creates_comment_relationship.set_source_node(author_node)
        author_creates_comment_relationship.set_destination_node(comment_node)
        author_creates_comment_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_creates_comment_relationship)

        # Construct PullRequestReviewComment -[COMMENTS_ON]-> PullRequestReview
        comment_review_relationship = CommentsOnPullRequestReview()
        comment_review_relationship.set_source_node(comment_node)
        comment_review_relationship.set_destination_node(self.get_parent().get_node())
        self.get_repo().get_preprocessor_storage().add_relationship(comment_review_relationship)

        reply_to_comment_data = self.get_data().get("replyTo", None)
        if reply_to_comment_data is not None and reply_to_comment_data.get("id", None) is not None:
            # Construct PullRequestReviewComment reply node
            replied_to_comment_node = PullRequestReviewComment().extract_and_update(
                {
                    "id": reply_to_comment_data.get("id")
                }
            )
            # Construct PullRequestReviewComment -[IS_REPLY_TO]-> PullRequestReviewComment relationship
            is_reply_to_relationship = IsReplyToPullRequestReviewComment()
            is_reply_to_relationship.set_source_node(comment_node)
            is_reply_to_relationship.set_destination_node(replied_to_comment_node)
            self.get_repo().get_preprocessor_storage().add_relationship(is_reply_to_relationship)


class SinglePullRequestReviewCommentProcessor(ProcessorTemplate):

    def process(self):
        # Construct pull request review comment node
        comment_node = PullRequestReviewComment().extract_and_update(self.get_data())
        # Update commit and original commit data in review node
        comment_commit_hash = self.get_data().get("commit", {}).get("oid", None)
        if comment_commit_hash is not None:
            comment_node.extract_and_update({"commitHash": comment_commit_hash})
        comment_original_commit_data = self.get_data().get("originalCommit", {}).get("oid", None)
        if comment_original_commit_data is not None:
            comment_node.extract_and_update({"originalCommitHash": comment_original_commit_data})
        self.get_repo().get_preprocessor_storage().add_node(comment_node)

        # Construct author node
        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)

        # Construct user -[CREATES_COMMENT]-> PullRequestReviewComment
        author_creates_comment_relationship = CreatesPullRequestReviewComment()
        author_creates_comment_relationship.set_source_node(author_node)
        author_creates_comment_relationship.set_destination_node(comment_node)
        author_creates_comment_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_creates_comment_relationship)

        # Construct PullRequestReviewComment -[SINGLE_COMMENTS_ON]-> PullRequest
        single_comment_pull_request_relationship = IsSinglePullRequestReviewComment()
        single_comment_pull_request_relationship.set_source_node(comment_node)
        single_comment_pull_request_relationship.set_destination_node(self.get_parent().get_parent().get_node())
        self.get_repo().get_preprocessor_storage().add_relationship(single_comment_pull_request_relationship)

        reply_to_comment_data = self.get_data().get("replyTo", None)
        if reply_to_comment_data is not None and reply_to_comment_data.get("id", None) is not None:
            # Construct PullRequestReviewComment reply node
            replied_to_comment_node = PullRequestReviewComment().extract_and_update(
                {
                    "id": reply_to_comment_data.get("id")
                }
            )
            # Construct PullRequestReviewComment -[IS_REPLY_TO]-> PullRequestReviewComment relationship
            is_reply_to_relationship = IsReplyToPullRequestReviewComment()
            is_reply_to_relationship.set_source_node(comment_node)
            is_reply_to_relationship.set_destination_node(replied_to_comment_node)
            self.get_repo().get_preprocessor_storage().add_relationship(is_reply_to_relationship)


class PullRequestFileProcessor(ProcessorTemplate):

    def process(self):
        # Construct pull request file node
        file_node = PullRequestFile().extract_and_update(self.get_data())
        file_node.extract_and_update({"pullRequestId": self.get_parent().get_node_id()})
        self.get_repo().get_preprocessor_storage().add_node(file_node)
        # Construct PullRequest -[PULL_REQUESTS_PROPOSES_CHANGE]-> PullRequestFile
        pull_request_file_change_relationship = PullRequestProposesFileChange()
        pull_request_file_change_relationship.set_source_node(self.get_parent().get_node())
        pull_request_file_change_relationship.set_destination_node(file_node)
        self.get_repo().get_preprocessor_storage().add_relationship(pull_request_file_change_relationship)
