import ckan.model as model
import ckan.plugins.toolkit as toolkit
import logging
import sqlalchemy

from ckan.common import config
from profanityfilter import ProfanityFilter
from ckan.common import c
from ckan.lib.base import render
from ckan.logic import check_access, get_action
from ckanext.datarequests import actions
from notification_models import CommentNotificationRecipient
from psycopg2 import ProgrammingError

_and_ = sqlalchemy.and_
log = logging.getLogger(__name__)


def threaded_comments_enabled():
    return toolkit.asbool(config.get('ckan.comments.threaded_comments', False))


def users_can_edit():
    return toolkit.asbool(config.get('ckan.comments.users_can_edit', False))


def profanity_check(cleaned_comment):
    more_words = load_bad_words()

    pf = ProfanityFilter(extra_censor_list=more_words)
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
        content_item_id,
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


def comment_notification_recipients_enabled():
    # @todo: check the database tables exist
    return True


def get_user_id():
    user = toolkit.c.userobj
    return user.id


def get_user_comment_follows(user_id, thread_id):
    return (
        model.Session.query(
            CommentNotificationRecipient
        )
        .filter(
            _and_(
                CommentNotificationRecipient.user_id == user_id,
                CommentNotificationRecipient.thread_id == thread_id
        ))
    )


def get_user_comment_follows_ids(user_id, thread_id):
    print('********** get_user_comment_follows_ids **********')
    following = []
    records = get_user_comment_follows(user_id, thread_id)

    from pprint import pprint
    for record in records:
        if record.comment_id:
            following.append(record.comment_id)
        else:
            following.append(record.thread_id)
        pprint(record)

    return list(set(following))


def add_comment_notification_recipient(data_dict):
    model.Session.add(CommentNotificationRecipient(**data_dict))
    model.Session.commit()


def remove_comment_notification_recipient(record):
    try:
        model.Session.delete(record)
        model.Session.commit()
    except Exception, e:
        log.error('Error removing `comment_notification_recipient` record:')
        log.error(str(e))


def add_user_to_comment_notifications(user_id, thread_id, comment_id=u''):
    # Is the user attempting to follow at the dataset/data request or the comment level?
    notification_level = 'top_level_comment' if comment_id else 'content_item'
    add_comment_notification_recipient({
        'user_id': user_id,
        'thread_id': thread_id,
        'comment_id': comment_id,
        'notification_level': notification_level
    })


def remove_all_comment_notification_recipient(user_id, thread_id):
    follows = get_user_comment_follows(user_id, thread_id)
    print('would remove these records')
    for record in follows:
        remove_comment_notification_recipient(record)
