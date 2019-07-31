import ckan.authz as authz
import ckan.model as model
import ckan.plugins.toolkit as toolkit
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

    def get_user_id(self):
        user = toolkit.c.userobj
        return user.id

    def get_existing_record(self, user_id, thread_id, comment_id=None):
        record = (
            model.Session.query(
                CommentNotificationRecipient
            )
            .filter(
                _and_(
                    CommentNotificationRecipient.user_id == user_id,
                    CommentNotificationRecipient.thread_id == thread_id,
                    CommentNotificationRecipient.comment_id == comment_id if comment_id else '',
                    CommentNotificationRecipient.action == 'follow',
            ))
        ).first()

        return record

    def add(self, data_dict):
        model.Session.add(CommentNotificationRecipient(**data_dict))
        model.Session.commit()

    def remove(self, record):
        model.Session.delete(record)
        model.Session.commit()

    def follow(self, thread_or_comment_id=None):
        """

        :param thread_or_comment_id: A UUID - can be either a thread ID or a specific top level comment id
        :return:
        """
        return self.follow_or_mute(thread_or_comment_id, 'follow')

    def mute(self, thread_or_comment_id=None):
        """

        :param thread_or_comment_id: A UUID - can be either a thread ID or a specific top level comment id
        :return:
        """
        return self.follow_or_mute(thread_or_comment_id, 'mute')

    def follow_or_mute(self, thread_or_comment_id, action):
        # Developers: Please note - within YTP comments, a "thread" represents a set of comments for a given dataset
        # or data request, whereas the meaning in the Jira story is different, i.e. it means a top level comment and
        # it's subsequent replies.
        if not self.valid_request_and_user(thread_or_comment_id):
            abort(404)

        thread, comment = self.get_thread_comment_or_both(thread_or_comment_id)

        if not thread or (comment and not thread):
            abort(404)

        # Is the user attempting to follow or mute at the dataset/data request or the sub-comment level?
        notification_level = 'secondary' if comment else 'primary'

        user_id = self.get_user_id()

        # Check for an existing record
        existing_record = self.get_existing_record(user_id, thread.id, comment.id if comment else None)

        if action == 'follow':
            if existing_record:
                return 'User %s already following thread %s' % (user_id, thread.id)
            else:
                self.add({
                    'user_id': user_id,
                    'thread_id': thread.id,
                    'comment_id': comment.id if comment else '',
                    'notification_level': notification_level,
                    'action': action
                })

                return 'User %s added to thread %s' % (user_id, thread.id)

        elif action == 'mute' and existing_record:
            self.remove(existing_record)

            return 'User %s removed from thread %s' % (user_id, thread.id)

