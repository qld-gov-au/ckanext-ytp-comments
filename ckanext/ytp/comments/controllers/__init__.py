# encoding: utf-8

""" Common functions used by both Pylons and Flask-based routing.

These functions should do the heavy lifting, with Pylons and Flask
specific modules just providing the integration hooks.
"""

import logging
import re

from ckan import model
from ckan.lib import captcha
from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import clean_dict, tuplize_dict, parse_params
from ckan.plugins.toolkit import _, abort, c, check_ckan_version, get_action, \
    h, request, render, ValidationError

from ckanext.ytp.comments import email_notifications, helpers, \
    model as comment_model, notification_helpers, request_helpers

log = logging.getLogger(__name__)


def _is_logged_in():
    if check_ckan_version('2.9'):
        from ckan.plugins.toolkit import g
        return g.user
    else:
        from ckan import authz
        return authz.auth_is_loggedin_user()


def _valid_request_and_user(thread_or_comment_id):
    """
    Check user logged in and perform simple validation of id provided in request
    :param thread_or_comment_id:
    :return:
    """
    return _is_logged_in() \
        and thread_or_comment_id \
        and not _contains_invalid_chars(thread_or_comment_id)


def _contains_invalid_chars(value):
    return re.search(r"[^0-9a-f-]", value)


def follow(thread_or_comment_id=None):
    """
    Add the user to the list of comment notification email recipients
    :param thread_or_comment_id: A UUID - can be either a thread ID or a specific top level comment ID
    :return:
    """
    return _follow_or_mute(thread_or_comment_id, 'follow')


def mute(thread_or_comment_id=None):
    """
    Remove the user from the list of comment notification email recipients
    :param thread_or_comment_id: A UUID - can be either a thread ID or a specific top level comment ID
    :return:
    """
    return _follow_or_mute(thread_or_comment_id, 'mute')


def _follow_or_mute(thread_or_comment_id, action):
    """
    *** Developers, please note: *** within YTP comments, a "thread" represents a set of comments for a given
    dataset or data request, whereas the meaning in the Jira story differs, i.e. it refers to a top level comment
    and it's subsequent replies. Where possible we use the code/YTP concept of "thread"

    :param thread_or_comment_id: UUID - can be either a thread ID (in the YTP sense) or a comment ID
    :param action: string - "follow" or "mute"
    :return:
    """
    if not _valid_request_and_user(thread_or_comment_id):
        return abort(404)

    thread, comment = notification_helpers.get_thread_comment_or_both(thread_or_comment_id)

    if not thread or (comment and not thread):
        return abort(404)

    notification_level = 'content_item' if not comment else 'top_level_comment'

    user_id = helpers.get_user_id()

    # Check for an existing record - helps us prevent re-adding the user to recipients table
    existing_record = notification_helpers.get_existing_record(user_id, thread.id, comment.id if comment else None)

    if action == 'follow':
        notification_helpers.process_follow_request(user_id, thread, comment, existing_record, notification_level)

    # User is muting comments at content item level or specific comment thread within that content item
    elif action == 'mute':
        notification_helpers.process_mute_request(user_id, thread, comment, existing_record, notification_level)

    # this should be called via AJAX, so we don't need to return a page
    return ""


def add(dataset_id, content_type='dataset'):
    return _add_or_reply('new', dataset_id, content_type)


def edit(content_type, content_item_id, comment_id):
    context = {'model': model, 'user': c.user}
    data_dict = {'id': content_item_id}

    # Auth check to make sure the user can see this content item
    helpers.check_content_access(content_type, context, data_dict)

    try:
        # Load the content item
        helpers.get_content_item(content_type, context, data_dict)
    except Exception:
        return abort(403)

    if request.method != 'POST':
        # get the form
        return helpers.render_content_template(content_type)

    data_dict = clean_dict(unflatten(
        tuplize_dict(parse_params(request_helpers.RequestHelper(request).get_post_params()))))
    data_dict['id'] = comment_id
    data_dict['content_type'] = content_type
    data_dict['content_item_id'] = content_item_id
    success = False
    try:
        get_action('comment_update')(context, data_dict)
        success = True
    except ValidationError as ve:
        log.debug("Validation Error", exc_info=True)
        if ve.error_dict and ve.error_dict.get('message'):
            msg = ve.error_dict['message']
        else:
            msg = str(ve)
        h.flash_error(msg)
    except Exception:
        log.debug("Exception", exc_info=True)
        return abort(403)

    return h.redirect_to(
        helpers.get_content_item_link(
            content_type,
            content_item_id if content_type == 'datarequest' else c.pkg.name,
            comment_id,
            'comment_' if success else 'edit_'
        ))


def reply(content_type, dataset_id, parent_id):
    c.action = 'reply'

    try:
        data = {'id': parent_id}
        c.parent_dict = get_action("comment_show")({'model': model, 'user': c.user},
                                                   data)
        c.parent = data['comment']
    except Exception:
        return abort(404)

    return _add_or_reply('reply', dataset_id, content_type, parent_id)


def _add_or_reply(comment_type, content_item_id, content_type='dataset', parent_id=None):
    """
    Allows the user to add a comment to an existing dataset or datarequest
    :param comment_type: Either 'new' or 'reply'
    :param content_item_id:
    :param content_type: string 'dataset' or 'datarequest'
    :return:
    """
    context = {'model': model, 'user': c.user}

    data_dict = {'id': content_item_id}

    # Auth check to make sure the user can see this content item
    helpers.check_content_access(content_type, context, data_dict)

    try:
        # Load the content item
        helpers.get_content_item(content_type, context, data_dict)
    except Exception:
        return abort(403)

    if request.method != 'POST':
        # get the form
        return helpers.render_content_template(content_type)

    data_dict = clean_dict(unflatten(
        tuplize_dict(parse_params(request_helpers.RequestHelper(request).get_post_params()))))
    data_dict['parent_id'] = c.parent.id if 'parent' in dir(c) else None

    data_dict['url'] = '/%s/%s' % (content_type, content_item_id if content_type == 'datarequest' else c.pkg.name)

    success = False
    try:
        captcha.check_recaptcha(request)
        res = get_action('comment_create')(context, data_dict)
        success = True
    except ValidationError as ve:
        log.debug("Validation Error", exc_info=True)
        if ve.error_dict and ve.error_dict.get('message'):
            msg = ve.error_dict['message']
        else:
            msg = str(ve)
        h.flash_error(msg)
    except captcha.CaptchaError:
        error_msg = _(u'Bad Captcha. Please try again.')
        h.flash_error(error_msg)
    except Exception:
        log.debug("Exception", exc_info=True)
        return abort(403)

    if success:
        email_notifications.notify_admins_and_comment_notification_recipients(
            helpers.get_org_id(content_type),
            c.userobj,
            'notification-new-comment',
            content_type,
            helpers.get_content_item_id(content_type),
            res['thread_id'],
            res['parent_id'] if comment_type == 'reply' else None,
            res['id'],
            c.datarequest['title'] if content_type == 'datarequest' else c.pkg_dict['title'],
            res['content']  # content is the comment that has been cleaned up in the action comment_create
        )

        if notification_helpers.comment_notification_recipients_enabled():
            if comment_type == 'reply':
                # Add the user who submitted the reply to comment notifications for this thread
                notification_helpers.add_commenter_to_comment_notifications(c.userobj.id, res['thread_id'],
                                                                            res['parent_id'])
            else:
                # Add the user who submitted the comment notifications for this new thread
                notification_helpers.add_commenter_to_comment_notifications(c.userobj.id, res['thread_id'], res['id'])

    if success:
        comment_id = res['id']
        anchor_prefix = 'comment_'
    elif comment_type == 'new':
        comment_id = None
        anchor_prefix = 'comment_form'
    else:
        comment_id = parent_id
        anchor_prefix = 'reply_'
    return h.redirect_to(
        helpers.get_content_item_link(
            content_type,
            content_item_id if content_type == 'datarequest' else c.pkg.name,
            comment_id, anchor_prefix
        ))


def delete(content_type, content_item_id, comment_id):
    context = {'model': model, 'user': c.user}
    data_dict = {'id': content_item_id}

    # Auth check to make sure the user can see this content item
    helpers.check_content_access(content_type, context, data_dict)

    try:
        # Load the content item
        helpers.get_content_item(content_type, context, data_dict)
    except Exception:
        return abort(403)

    try:
        data_dict = {'id': comment_id, 'content_type': content_type, 'content_item_id': content_item_id}
        get_action('comment_delete')(context, data_dict)
    except Exception as e:
        log.debug("Exception", exc_info=True)
        if e.error_dict and e.error_dict.get('message'):
            msg = e.error_dict['message']
        else:
            msg = str(e)
        h.flash_error(msg)

    return h.redirect_to(
        helpers.get_content_item_link(
            content_type,
            content_item_id if content_type == 'datarequest' else c.pkg.name,
            comment_id
        ))


def flag(comment_id):
    if _is_logged_in():
        # Using the comment model rather than the update action because update action updates modified timestamp
        comment = comment_model.Comment.get(comment_id)
        if comment and not comment.flagged:
            comment.flagged = True
            model.Session.add(comment)
            model.Session.commit()
            email_notifications.flagged_comment_notification(comment)
    return ""


def unflag(content_type, content_item_id, comment_id):
    """
    Remove the 'flagged' attribute on a comment
    :param content_type: string 'dataset' or 'datarequest'
    :param content_item_id: string
    :param comment_id: string ID of the comment to unflag
    :return:
    """
    context = {'model': model, 'user': c.user}

    # Using the comment model rather than the update action because update action updates modified timestamp
    comment = comment_model.Comment.get(comment_id)

    if not comment \
            or not comment.flagged \
            or not _is_logged_in() \
            or not helpers.user_can_manage_comments(content_type, content_item_id):
        return abort(403)

    comment.flagged = False

    model.Session.add(comment)
    model.Session.commit()

    h.flash_success(_('Comment un-flagged'))

    data_dict = {'id': content_item_id}

    if content_type == 'datarequest':
        c.datarequest = get_action('show_datarequest')(context, data_dict)
    else:
        c.pkg_dict = get_action('package_show')(context, data_dict)
        c.pkg = context['package']
    return h.redirect_to(
        helpers.get_content_item_link(
            content_type,
            content_item_id if content_type == 'datarequest' else c.pkg.name,
            comment_id
        ))


def dataset_comments(content_type, id):
    context = {'model': model, 'user': c.user}

    data_dict = {'id': id}
    content_type = content_type or 'dataset'
    # Auth check to make sure the user can see this content item
    helpers.check_content_access(content_type, context, data_dict)

    try:
        # Load the content item
        helpers.get_content_item(content_type, context, data_dict)
    except Exception:
        return abort(403)
    return render('package/comments.html', extra_vars={
        'pkg': c.pkg, 'pkg_dict': c.pkg_dict, 'content_type': content_type})
