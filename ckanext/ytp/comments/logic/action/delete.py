# encoding: utf-8

import logging

from ckan.plugins.toolkit import abort, check_access, get_or_bust

import ckanext.ytp.comments.model as comment_model
from . import _trigger_package_index_on_comment

log = logging.getLogger(__name__)


def comment_delete(context, data_dict):
    model = context['model']
    user = context['user']
    userobj = model.User.get(user)

    check_access("comment_delete", context, data_dict)

    # Comment should either be set state=='deleted' if no children,
    # otherwise content should be set to withdrawn text
    id = get_or_bust(data_dict, 'id')
    comment = comment_model.Comment.get(id)
    if not comment:
        return abort(404)

    comment.state = 'deleted'
    comment.deleted_by_user_id = userobj.id

    model.Session.add(comment)
    model.Session.commit()

    _trigger_package_index_on_comment(comment.thread_id)

    return {'success': True}
