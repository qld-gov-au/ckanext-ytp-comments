# encoding: utf-8

import logging

from ckan.plugins.toolkit import _, get_or_bust

from ckanext.ytp.comments import helpers, model as comment_model


log = logging.getLogger(__name__)


def comment_delete(context, data_dict):
    model = context['model']
    user = context['user']

    userobj = model.User.get(user)
    # If sysadmin.
    if userobj and userobj.sysadmin:
        return {'success': True}

    cid = get_or_bust(data_dict, 'id')

    comment = comment_model.Comment.get(cid)
    if not comment:
        return {'success': False, 'msg': _('Comment does not exist')}

    content_type = data_dict.get('content_type', None)
    content_item_id = data_dict.get('content_item_id', None)

    if content_type and content_item_id:
        if not helpers.user_can_manage_comments(content_type, content_item_id):
            return {'success': False, 'msg': _('User is not authorised to delete this comment')}
        else:
            return {'success': True}

    if comment.user_id is not userobj.id:
        return {'success': False, 'msg': _('User is not the author of the comment')}

    return {'success': True}
