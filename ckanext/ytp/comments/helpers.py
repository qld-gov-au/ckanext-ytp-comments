# encoding: utf-8

import logging
import sqlalchemy

from ckan import model
from ckan.plugins.toolkit import asbool, c, h, config, check_access, \
    get_action, render, render_snippet, url_for
from profanityfilter import ProfanityFilter

_and_ = sqlalchemy.and_
log = logging.getLogger(__name__)


def _is_action_configured(name):
    try:
        return get_action(name) is not None
    except KeyError:
        return False


def threaded_comments_enabled():
    return asbool(config.get('ckan.comments.threaded_comments', False))


def users_can_edit():
    return asbool(config.get('ckan.comments.users_can_edit', False))


def show_comments_tab_page():
    return asbool(config.get('ckan.comments.show_comments_tab_page', False))


def profanity_check(cleaned_comment):
    if not cleaned_comment:
        return False
    custom_profanity_list = config.get('ckan.comments.profanity_list', [])

    if custom_profanity_list:
        pf = ProfanityFilter(custom_censor_list=custom_profanity_list.splitlines())
    else:
        # Fall back to original behaviour of built-in Profanity bad words list
        # combined with bad_words_file and good_words_file
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
        from ckanext.datarequests import actions
        c.datarequest = actions.show_datarequest(context, data_dict)
    else:
        data_dict['include_tracking'] = True
        c.pkg_dict = get_action('package_show')(context, data_dict)
        c.pkg = context['package']


def check_content_access(content_type, context, data_dict):
    check_access('show_datarequest' if content_type == 'datarequest' else 'package_show', context, data_dict)


def get_content_item_link(content_type, content_item_id, comment_id=None, anchor_prefix='comment_'):
    """
    Get a fully qualified URL to the content item being commented on.

    :param content_type: string Currently only supports 'dataset' or 'datarequest'
    :param content_item_id: string Package name, or Data Request ID
    :param comment_id: string `comment`.`id`
    :return:
    """
    kwargs = {'id': content_item_id, 'qualified': True}
    if content_type == 'datarequest':
        route_name = 'datarequest.comment'
    elif asbool(config.get('ckan.comments.show_comments_tab_page', False)):
        route_name = 'comments.list'
        kwargs['content_type'] = content_type
    else:
        route_name = ('{}.read').format(content_type)
    url = url_for(route_name, **kwargs)
    if comment_id:
        url = '{}#{}{}'.format(url, anchor_prefix, comment_id)
    elif anchor_prefix != 'comment_':
        url = '{}#{}'.format(url, anchor_prefix)
    return url


def render_content_template(content_type):
    return render(
        'datarequests/comment.html' if content_type == 'datarequest' else "package/read.html",
        extra_vars={'pkg': c.pkg, 'pkg_dict': c.pkg_dict}
    )


def user_can_edit_comment(comment_user_id):
    user = c.userobj
    if user and comment_user_id == user.id and users_can_edit():
        return True
    return False


def user_can_manage_comments(content_type, content_item_id):
    return h.check_access(
        'update_datarequest' if content_type == 'datarequest' else 'package_update',
        {'id': content_item_id})


def get_org_id(content_type):
    return c.datarequest['organization_id'] if content_type == 'datarequest' else c.pkg.owner_org


def get_content_item_id(content_type):
    return c.datarequest['id'] if content_type == 'datarequest' else c.pkg.name


def get_user_id():
    user = c.userobj
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
    return render_snippet('snippets/count_badge.html', {'count': comments_count})


def is_reporting_enabled():
    return _is_action_configured('report_list')


def unreplied_comments_x_days(thread_url):
    """A helper function for Engagement Reporting
    to highlight un-replied comments after x number of days.
    (Number of days is a constant in the reporting plugin)
    """
    comment_ids = []

    if is_reporting_enabled():
        unreplied_comments = get_action(
            'comments_no_replies_after_x_days'
        )({}, {'thread_url': thread_url})

        comment_ids = [comment[1] for comment in unreplied_comments]

    return comment_ids


def get_comment_notification_recipients_enabled():
    return config.get('ckan.comments.follow_mute_enabled', False)
