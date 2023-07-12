# encoding: utf-8

import logging

from ckan.plugins.toolkit import abort, check_access, check_ckan_version, get_or_bust

import ckanext.ytp.comments.model as comment_model

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

    comment_dict = comment.as_dict()
    if check_ckan_version('2.10'):
        thread_id = comment_dict["thread_id"]
        log.debug("Notifying subscribers of comment deletion on thread [%s]", thread_id)
        from ckanext.ytp.comments import signals
        signals.deleted.send(thread_id, comment=comment_dict)

    return {'success': True}
