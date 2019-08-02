import ckan.authz as authz
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import helpers
import model as comment_model
import sqlalchemy
import re

from ckan.lib.base import BaseController, abort
from notification_models import CommentNotificationRecipient

_and_ = sqlalchemy.and_


class NotificationController(BaseController):

    def valid_request_and_user(self, thread_or_comment_id):
        """
        Check user logged in and perform simple validation of id provided in request
        :param thread_or_comment_id:
        :return:
        """
        return False if not authz.auth_is_loggedin_user() \
                or not id \
                or self.contains_invalid_chars(thread_or_comment_id) else True

    def contains_invalid_chars(self, value):
        return re.search(r"[^0-9a-f-]", value)

    def get_thread_comment_or_both(self, thread_or_comment_id):
        # Check if provided id is for a thread..
        thread = comment_model.CommentThread.get(thread_or_comment_id)

        if thread:
            comment = None
        else:
            # Fallback: check for comment by id provided...
            comment = comment_model.Comment.get(thread_or_comment_id)
            if comment:
                thread = comment_model.CommentThread.get(comment.thread_id)

        return thread, comment

    def get_existing_record(self, user_id, thread_id, comment_id=None):
        # Condition doesn't seem to get set properly within _and_ filter
        if not comment_id:
            comment_id = u''

        record = (
            model.Session.query(
                CommentNotificationRecipient
            )
            .filter(
                _and_(
                    CommentNotificationRecipient.user_id == user_id,
                    CommentNotificationRecipient.thread_id == thread_id,
                    CommentNotificationRecipient.comment_id == comment_id
            ))
        ).first()

        return record

    def follow(self, thread_or_comment_id=None):
        """
        Add the user to the list of comment notification email recipients
        :param thread_or_comment_id: A UUID - can be either a thread ID or a specific top level comment ID
        :return:
        """
        return self.follow_or_mute(thread_or_comment_id, 'follow')

    def mute(self, thread_or_comment_id=None):
        """
        Remove the user from the list of comment notification email recipients
        :param thread_or_comment_id: A UUID - can be either a thread ID or a specific top level comment ID
        :return:
        """
        return self.follow_or_mute(thread_or_comment_id, 'mute')

    def follow_or_mute(self, thread_or_comment_id, action):
        """
        *** Developers, please note: *** within YTP comments, a "thread" represents a set of comments for a given
        dataset or data request, whereas the meaning in the Jira story is different, i.e. it means a top level comment
        and it's subsequent replies. Where possible we use the code/YTP concept of "thread"

        :param thread_or_comment_id: UUID - can be either a thread ID (in the YTP sense) or a comment ID
        :param action: string - "follow" or "mute"
        :return:
        """
        if not self.valid_request_and_user(thread_or_comment_id):
            abort(404)

        thread, comment = self.get_thread_comment_or_both(thread_or_comment_id)

        if not thread or (comment and not thread):
            abort(404)

        user_id = helpers.get_user_id()

        # Check for an existing record - helps us prevent re-adding the user to recipients table
        existing_record = self.get_existing_record(user_id, thread.id, comment.id if comment else None)

        if action == 'follow':
            if existing_record:
                return 'User %s already following thread %s' % (user_id, thread.id)
            else:
                helpers.add_user_to_comment_notifications(user_id, thread.id, comment.id if comment else u'')
                return 'User %s added to thread %s' % (user_id, thread.id)
        # User is muting comments at the dataset/data request level or specific comment thread within that content item
        elif action == 'mute' and existing_record:
            # When a user mutes comments at the dataset/data request level we remove ALL entries for that user
            # in the `comment_notification_recipient` table for the matching YTP thread.id
            if not comment:
                helpers.remove_all_comment_notification_recipient(user_id, thread.id)
            elif existing_record:
                helpers.remove_comment_notification_recipient(existing_record)

            return 'User %s removed from thread %s' % (user_id, thread.id)

