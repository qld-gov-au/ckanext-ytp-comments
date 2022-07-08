# encoding: utf-8

import logging

from ckan.plugins.toolkit import _, get_or_bust

from ckanext.ytp.comments import helpers, model as comment_model

log = logging.getLogger(__name__)


def comment_update(context, data_dict):
    user = context['user']
    model = context['model']

    userobj = model.User.get(user)

    if not userobj:
        log.debug("User is not logged in")
        return {'success': False, 'msg': _('You must be logged in to add a comment')}

    cid = get_or_bust(data_dict, 'id')

    comment = comment_model.Comment.get(cid)
    if not comment:
        return {'success': False, 'msg': _('Comment does not exist')}

    content_type = data_dict.get('content_type', None)
    content_item_id = data_dict.get('content_item_id', None)

    if content_type and content_item_id:
        if helpers.user_can_manage_comments(content_type, content_item_id):
            return {'success': True}
        else:
            return {'success': False, 'msg': _('User is not authorised to edit this comment')}

    if comment.user_id != userobj.id:
        return {'success': False, 'msg': _('User is not the author of the comment')}

    return {'success': True}
