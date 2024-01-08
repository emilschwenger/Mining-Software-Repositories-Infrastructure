from src.DataProcessing.ProcessorTemplate import ProcessorTemplate, ProcessorTemplateRoot
from src.DatabaseObjects.DatabaseNode.Discussion import Discussion, DiscussionComment
from src.DatabaseObjects.DatabaseNode.User import User
from src.DatabaseObjects.DatabaseNode.Label import Label
from src.DatabaseObjects.DatabaseNode.Project import Project
from src.DatabaseObjects.DatabaseRelationship.User import CreatesDiscussion, CreatesDiscussionComment
from src.DatabaseObjects.DatabaseRelationship.Discussion import DiscussionHasLabel, DiscussionHasComment, \
    ReplyToDiscussionComment, CommentAnswersDiscussion
from src.DatabaseObjects.DatabaseRelationship.Project import ProjectHasDiscussion


class DiscussionProcessorRoot(ProcessorTemplateRoot):

    def process(self):
        for discussion in self.get_data().get("nodes", None):
            single_discussion = DiscussionProcessor(self.get_repo(), discussion, self)
            single_discussion.process()


class DiscussionProcessor(ProcessorTemplate):

    def process(self):
        # Construct project node
        project_node = Project().extract_and_update({
            "id": self.get_repo().get_project_id()
        })

        # Create the current discussion node
        discussion_node = Discussion().extract_and_update(self.get_data())
        discussion_category_name = self.get_data().get("category", {}).get("name", "")
        discussion_node.extract_and_update({"categoryName": discussion_category_name})
        self.get_repo().get_preprocessor_storage().add_node(discussion_node)
        self.set_node(discussion_node)

        # Construct Project-[:PROJECT_HAS_DISCUSSION]->Discussion relationship
        project_discussion_relationship = ProjectHasDiscussion()
        project_discussion_relationship.set_source_node(project_node)
        project_discussion_relationship.set_destination_node(discussion_node)
        self.get_repo().get_preprocessor_storage().add_relationship(project_discussion_relationship)

        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()

        # Construct author node
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)

        # Construct user -[CREATES_DISCUSSION]-> discussion
        author_discussion_relationship = CreatesDiscussion()
        author_discussion_relationship.set_source_node(author_node)
        author_discussion_relationship.set_destination_node(discussion_node)
        author_discussion_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_discussion_relationship)

        # Process label data
        label_data = self.get_data().get("labels", None)
        for label_item in label_data.get("nodes", []):
            if label_item is None:
                continue
            discussion_label_processor = DiscussionLabelProcessor(self.get_repo(), label_item, self)
            discussion_label_processor.process()

        # Process discussion comment data
        comments_data = self.get_data().get("comments", None)
        for comment_item in comments_data.get("nodes", []):
            if comment_item is None:
                continue
            discussion_comment_processor = DiscussionCommentsProcessor(self.get_repo(), comment_item, self)
            discussion_comment_processor.process()


class DiscussionLabelProcessor(ProcessorTemplate):

    def process(self):
        # Create the label node
        label_node = Label().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(label_node)

        # Create discussion -[HAS_LABEL]-> Relationship
        discussion_label_relationship = DiscussionHasLabel()
        discussion_label_relationship.set_source_node(self.get_parent().get_node())
        discussion_label_relationship.set_destination_node(label_node)
        self.get_repo().get_preprocessor_storage().add_relationship(discussion_label_relationship)


class DiscussionCommentsProcessor(ProcessorTemplate):

    def process(self):
        # Create the discussion comment node
        comment_node = DiscussionComment().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(comment_node)
        self.set_node(comment_node)

        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        # Construct author node
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)

        # Construct user -[CREATES_DISCUSSION_COMMENT]-> DiscussionComment relationship
        author_comment_relationship = CreatesDiscussionComment()
        author_comment_relationship.set_source_node(author_node)
        author_comment_relationship.set_destination_node(comment_node)
        author_comment_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_comment_relationship)

        # Create Discussion -[HAS_COMMENT]-> DiscussionComment relationship
        discussion_comment_relationship = DiscussionHasComment()
        discussion_comment_relationship.set_source_node(self.get_parent().get_node())
        discussion_comment_relationship.set_destination_node(comment_node)
        self.get_repo().get_preprocessor_storage().add_relationship(discussion_comment_relationship)

        # Create DiscussionComment -[ANSWERS_DISCUSSION]-> Discussion relationship
        comment_answers_discussion = self.get_data().get("isAnswer", False)
        if comment_answers_discussion:
            comment_answers_discussion_relationship = CommentAnswersDiscussion()
            comment_answers_discussion_relationship.set_source_node(comment_node)
            comment_answers_discussion_relationship.set_destination_node(self.get_parent().get_node())
            self.get_repo().get_preprocessor_storage().add_relationship(comment_answers_discussion_relationship)

        # Process discussion comment data
        replies_data = self.get_data().get("replies", None)
        for reply_item in replies_data.get("nodes", []):
            if reply_item is None:
                continue
            comment_reply_processor = DiscussionRepliesProcessor(self.get_repo(), reply_item, self)
            comment_reply_processor.process()


class DiscussionRepliesProcessor(ProcessorTemplate):

    def process(self):
        # Create the discussion comment node
        comment_node = DiscussionComment().extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_node(comment_node)
        self.set_node(comment_node)

        author_data = self.get_data().get("author", None)
        if author_data is None:
            author_data = User.get_default_user_data()
        # Construct author node
        author_node = User().extract_and_update(author_data)
        self.get_repo().get_preprocessor_storage().add_node(author_node)

        # Construct user -[CREATES_DISCUSSION_COMMENT]-> DiscussionComment relationship
        author_comment_relationship = CreatesDiscussionComment()
        author_comment_relationship.set_source_node(author_node)
        author_comment_relationship.set_destination_node(comment_node)
        author_comment_relationship.extract_and_update(self.get_data())
        self.get_repo().get_preprocessor_storage().add_relationship(author_comment_relationship)

        # Create DiscussionComment -[REPLY_TO_COMMENT]-> DiscussionComment
        reply_to_comment_relationship = ReplyToDiscussionComment()
        reply_to_comment_relationship.set_source_node(comment_node)
        reply_to_comment_relationship.set_destination_node(self.get_parent().get_node())
        self.get_repo().get_preprocessor_storage().add_relationship(reply_to_comment_relationship)

        # Create Discussion -[HAS_COMMENT]-> DiscussionComment relationship
        discussion_comment_relationship = DiscussionHasComment()
        discussion_comment_relationship.set_source_node(self.get_parent().get_parent().get_node())
        discussion_comment_relationship.set_destination_node(comment_node)
        self.get_repo().get_preprocessor_storage().add_relationship(discussion_comment_relationship)
