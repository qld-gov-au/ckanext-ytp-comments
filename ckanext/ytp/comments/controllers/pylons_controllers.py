# encoding: utf-8

from ckan.plugins.toolkit import BaseController

from ckanext.ytp.comments.controllers import add, edit, reply, delete, \
    flag, unflag, dataset_comments, follow, mute


class CommentController(BaseController):

    def add(self, dataset_id, content_type='dataset'):
        return add(dataset_id, content_type)

    def edit(self, content_type, content_item_id, comment_id):
        return edit(content_type, content_item_id, comment_id)

    def reply(self, content_type, dataset_id, parent_id):
        return reply(content_type, dataset_id, parent_id)

    def delete(self, content_type, content_item_id, comment_id):
        return delete(content_type, content_item_id, comment_id)

    def flag(self, comment_id):
        return flag(comment_id)

    def unflag(self, content_type, content_item_id, comment_id):
        return unflag(content_type, content_item_id, comment_id)

    def dataset_comments(self, content_type, id):
        return dataset_comments(content_type, id)


class NotificationController(BaseController):

    def follow(self, thread_or_comment_id=None):
        return follow(thread_or_comment_id)

    def mute(self, thread_or_comment_id=None):
        return mute(thread_or_comment_id)
