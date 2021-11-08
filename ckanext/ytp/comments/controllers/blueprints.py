# encoding: utf-8

from flask import Blueprint

from ckanext.ytp.comments import helpers
from ckanext.ytp.comments.controllers import add, edit, reply, delete,\
    flag, unflag, dataset_comments, follow, mute


commenting = Blueprint(
    u'comments',
    __name__
)

if helpers.show_comments_tab_page():
    commenting.add_url_rule('/dataset/<dataset_id>/comments', 'dataset_comments', view_func=dataset_comments)
commenting.add_url_rule('/<dataset_id>/comments/add', view_func=add)
commenting.add_url_rule('/<content_type>/<dataset_id>/comments/add', view_func=add)
commenting.add_url_rule('/<content_type>/<content_item_id>/comments/<comment_id>/edit', view_func=edit)
commenting.add_url_rule('/<content_type>/<dataset_id>/comments/<parent_id>/reply', view_func=reply)
commenting.add_url_rule('/<content_type>/<content_item_id>/comments/<comment_id>/delete', view_func=delete)
commenting.add_url_rule('/comment/<comment_id>/flag', view_func=flag)
commenting.add_url_rule('/<content_type>/<content_item_id>/comments/<comment_id>/unflag', view_func=unflag)
commenting.add_url_rule('/comments/<thread_or_comment_id>/follow', view_func=follow)
commenting.add_url_rule('/comments/<thread_or_comment_id>/mute', view_func=mute)


def get_blueprints():
    return [commenting]
