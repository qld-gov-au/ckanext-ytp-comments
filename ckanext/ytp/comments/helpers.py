import ckan.plugins.toolkit as toolkit
import re

from ckan.common import config, request
from profanity import profanity
from ckan.common import c
from ckan.lib.base import render
from ckan.logic import check_access, get_action
from ckanext.datarequests import actions


def threaded_comments_enabled():
    return toolkit.asbool(config.get('ckan.comments.threaded_comments', False))


def users_can_edit():
    return toolkit.asbool(config.get('ckan.comments.users_can_edit', False))


def profanity_check(cleaned_comment):
    profanity.load_words(load_bad_words())
    return profanity.contains_profanity(cleaned_comment)


def load_bad_words():
    filepath = config.get('ckan.comments.bad_words_file', None)
    if not filepath:
        # @todo: dynamically set this path
        filepath = '/usr/lib/ckan/default/src/ckanext-ytp-comments/ckanext/ytp/comments/bad_words.txt'

    f = open(filepath, 'r')
    x = f.read().splitlines()
    f.close()
    return x


def get_content_item(content_type, context, data_dict):
    if content_type == 'datarequest':
        c.datarequest = actions.show_datarequest(context, data_dict)
    else:
        data_dict['include_tracking'] = True
        c.pkg_dict = get_action('package_show')(context, data_dict)
        c.pkg = context['package']


def check_content_access(content_type, context, data_dict):
    if content_type == 'dataset':
        check_access('package_show', context, data_dict)
    elif content_type == 'datareqest':
        check_access('show_datarequest', context, data_dict)


def get_redirect_url(content_type, content_item_id, anchor):
    if content_type == 'datarequest':
        return str('/datarequest/comment/%s#%s' % (content_item_id, anchor))
    else:
        return str('/dataset/%s#%s' % (content_item_id, anchor))


def render_content_template(content_type):
    return render(
        'datarequests/comment.html' if content_type == 'datarequest' else "package/read.html"
    )


def user_can_edit_comment(comment_user_id):
    user = toolkit.c.userobj
    if user and comment_user_id == user.id and users_can_edit():
        return True
    return False


def user_can_manage_comments(content_type, content_item_id):
    if content_type == 'datarequest':
        return toolkit.h.check_access('update_datarequest', {'id': content_item_id})
    elif content_type == 'dataset':
        return toolkit.h.check_access('package_update', {'id': content_item_id})
    return False


def get_org_id(content_type):
    return c.datarequest['organization_id'] if content_type == 'datarequest' else c.pkg.owner_org