import ckan.plugins.toolkit as toolkit
import logging
import sqlalchemy

from ckan.common import config
from profanityfilter import ProfanityFilter
from ckan.common import c
from ckan.lib.base import render
from ckan.logic import check_access, get_action
from ckanext.datarequests import actions
import ckan.model as model

_and_ = sqlalchemy.and_
log = logging.getLogger(__name__)


def threaded_comments_enabled():
    return toolkit.asbool(config.get('ckan.comments.threaded_comments', False))


def users_can_edit():
    return toolkit.asbool(config.get('ckan.comments.users_can_edit', False))


def show_comments_tab_page():
    return toolkit.asbool(config.get('ckan.comments.show_comments_tab_page', False))


def profanity_check(cleaned_comment):
    more_words = load_bad_words()
    whitelist_words = load_good_words()

    pf = ProfanityFilter(extra_censor_list=more_words)
    for word in whitelist_words:
        pf.remove_word(word)
    return pf.is_profane(cleaned_comment)


def load_bad_words():
    filepath = config.get('ckan.comments.bad_words_file', None)
    if not filepath:
        import os
        filepath = os.path.dirname(os.path.realpath(__file__)) + '/bad_words.txt'
    f = open(filepath, 'r')
    x = f.read().splitlines()
    f.close()
    return x


def load_good_words():
    filepath = config.get('ckan.comments.good_words_file', None)
    if not filepath:
        import os
        filepath = os.path.dirname(os.path.realpath(__file__)) + '/good_words.txt'
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
    check_access('show_datarequest' if content_type == 'datarequest' else 'package_show', context, data_dict)


def get_redirect_url(content_type, content_item_id, anchor):
    return '/%s/%s#%s' % (
        'datarequest/comment' if content_type == 'datarequest' else 'dataset',
        content_item_id + '/comments' if show_comments_tab_page() else content_item_id,
        anchor
    )


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


def get_content_item_id(content_type):
    return c.datarequest['id'] if content_type == 'datarequest' else c.pkg.name


def get_user_id():
    user = toolkit.c.userobj
    return user.id


def get_comment_thread(dataset_name, content_type='dataset'):
    url = '/%s/%s' % (content_type, dataset_name)
    return get_action('thread_show')({'model': model, 'with_deleted': True}, {'url': url})


def get_comment_count_for_dataset(dataset_name, content_type='dataset'):
    url = '/%s/%s' % (content_type, dataset_name)
    count = get_action('comment_count')({'model': model}, {'url': url})
    return count


def get_content_type_comments_badge(dataset_name, content_type='dataset'):
    comments_count = get_comment_count_for_dataset(dataset_name, content_type)
    return toolkit.render_snippet('snippets/count_badge.html',  {'count': comments_count})