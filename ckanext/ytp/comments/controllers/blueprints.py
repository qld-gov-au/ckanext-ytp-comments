# encoding: utf-8

from flask import Blueprint

from ckanext.ytp.comments import helpers
from ckanext.ytp.comments.controllers import add, edit, reply, delete, \
    flag, unflag, dataset_comments, follow, mute


commenting = Blueprint(
    u'comments',
    __name__
)

if helpers.show_comments_tab_page():
    commenting.add_url_rule('/<content_type>/<id>/comments', 'list', view_func=dataset_comments)
commenting.add_url_rule('/<dataset_id>/comments/add', view_func=add, methods=('GET', 'POST'))
commenting.add_url_rule('/<content_type>/<dataset_id>/comments/add', view_func=add, methods=('GET', 'POST'))
commenting.add_url_rule('/<content_item_id>/comments/<comment_id>/edit', view_func=edit, methods=('GET', 'POST'))
commenting.add_url_rule('/<content_type>/<content_item_id>/comments/<comment_id>/edit', view_func=edit, methods=('GET', 'POST'))
commenting.add_url_rule('/<dataset_id>/comments/<parent_id>/reply', view_func=reply, methods=('GET', 'POST'))
commenting.add_url_rule('/<content_type>/<dataset_id>/comments/<parent_id>/reply', view_func=reply, methods=('GET', 'POST'))
commenting.add_url_rule('/<content_item_id>/comments/<comment_id>/delete', view_func=delete, methods=('GET', 'POST'))
commenting.add_url_rule('/<content_type>/<content_item_id>/comments/<comment_id>/delete', view_func=delete, methods=('GET', 'POST'))
commenting.add_url_rule('/comment/<comment_id>/flag', view_func=flag, methods=('GET', 'POST'))
commenting.add_url_rule('/<content_item_id>/comments/<comment_id>/unflag', view_func=unflag, methods=('GET', 'POST'))
commenting.add_url_rule('/<content_type>/<content_item_id>/comments/<comment_id>/unflag', view_func=unflag, methods=('GET', 'POST'))
commenting.add_url_rule('/comments/<thread_or_comment_id>/follow', view_func=follow, methods=('GET', 'POST'))
commenting.add_url_rule('/comments/<thread_or_comment_id>/mute', view_func=mute, methods=('GET', 'POST'))


def get_blueprints():
    return [commenting]
