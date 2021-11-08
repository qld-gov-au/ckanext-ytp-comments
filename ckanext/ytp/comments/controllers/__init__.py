# encoding: utf-8

import logging
import re

from ckan import authz, model
from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import clean_dict, tuplize_dict, parse_params
from ckan.plugins import toolkit
from ckan.plugins.toolkit import _, abort, c, get_action, h, request, ValidationError

from ckanext.ytp.comments import email_notifications, helpers,\
    model as comment_model, notification_helpers


log = logging.getLogger(__name__)


def _valid_request_and_user(thread_or_comment_id):
    """
    Check user logged in and perform simple validation of id provided in request
    :param thread_or_comment_id:
    :return:
    """
    return False if not authz.auth_is_loggedin_user() \
        or not id \
        or _contains_invalid_chars(thread_or_comment_id) else True


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
        toolkit.abort(404)

    thread, comment = notification_helpers.get_thread_comment_or_both(thread_or_comment_id)

    if not thread or (comment and not thread):
        toolkit.abort(404)

    notification_level = 'content_item' if not comment else 'top_level_comment'

    user_id = helpers.get_user_id()

    # Check for an existing record - helps us prevent re-adding the user to recipients table
    existing_record = notification_helpers.get_existing_record(user_id, thread.id, comment.id if comment else None)

    if action == 'follow':
        notification_helpers.process_follow_request(user_id, thread, comment, existing_record, notification_level)

    # User is muting comments at content item level or specific comment thread within that content item
    elif action == 'mute':
        notification_helpers.process_mute_request(user_id, thread, comment, existing_record, notification_level)


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
    except:
        abort(403)

    if request.method == 'POST':
        data_dict = clean_dict(unflatten(
            tuplize_dict(parse_params(request.POST))))
        data_dict['id'] = comment_id
        data_dict['content_type'] = content_type
        data_dict['content_item_id'] = content_item_id
        success = False
        try:
            get_action('comment_update')(context, data_dict)
            success = True
        except ValidationError as ve:
            log.debug(ve)
            if ve.error_dict and ve.error_dict.get('message'):
                msg = ve.error_dict['message']
            else:
                msg = str(ve)
            h.flash_error(msg)
        except Exception as e:
            log.debug(e)
            abort(403)

        h.redirect_to(
            helpers.get_redirect_url(
                content_type,
                content_item_id if content_type == 'datarequest' else c.pkg.name,
                'comment_' + str(comment_id) if success else 'edit_' + str(comment_id)
            ))

    return helpers.render_content_template(content_type)


def reply(content_type, dataset_id, parent_id):
    c.action = 'reply'

    try:
        data = {'id': parent_id}
        c.parent_dict = get_action("comment_show")({'model': model, 'user': c.user},
                                                   data)
        c.parent = data['comment']
    except:
        abort(404)

    return _add_or_reply('reply', dataset_id, content_type, parent_id)


def _add_or_reply(comment_type, content_item_id, content_type, parent_id=None):
    """
    Allows the user to add a comment to an existing dataset or datarequest
    :param comment_type:
    :param content_item_id:
    :param content_type: string 'dataset' or 'datarequest'
    :return:
    """
    content_type = 'dataset' if 'content_type' not in vars() else content_type

    context = {'model': model, 'user': c.user}

    data_dict = {'id': content_item_id}

    # Auth check to make sure the user can see this content item
    helpers.check_content_access(content_type, context, data_dict)

    try:
        # Load the content item
        helpers.get_content_item(content_type, context, data_dict)
    except:
        abort(403)

    if request.method == 'POST':
        data_dict = clean_dict(unflatten(
            tuplize_dict(parse_params(request.POST))))
        data_dict['parent_id'] = c.parent.id if c.parent else None

        data_dict['url'] = '/%s/%s' % (content_type, content_item_id if content_type == 'datarequest' else c.pkg.name)

        success = False
        try:
            res = get_action('comment_create')(context, data_dict)
            success = True
        except ValidationError as ve:
            log.debug(ve)
            if ve.error_dict and ve.error_dict.get('message'):
                msg = ve.error_dict['message']
            else:
                msg = str(ve)
            h.flash_error(msg)
        except Exception as e:
            log.debug(e)
            abort(403)

        if success:
            email_notifications.notify_admins_and_comment_notification_recipients(
                helpers.get_org_id(content_type),
                toolkit.c.userobj,
                'notification-new-comment',
                content_type,
                helpers.get_content_item_id(content_type),
                res['thread_id'],
                res['parent_id'] if comment_type == 'reply' else None,
                res['id'],
                c.pkg_dict['title'] if content_type == 'dataset' else c.datarequest['title'],
                res['content']  # content is the comment that has been cleaned up in the action comment_create
            )

            if notification_helpers.comment_notification_recipients_enabled():
                if comment_type == 'reply':
                    # Add the user who submitted the reply to comment notifications for this thread
                    notification_helpers.add_commenter_to_comment_notifications(toolkit.c.userobj.id, res['thread_id'], res['parent_id'])
                else:
                    # Add the user who submitted the comment notifications for this new thread
                    notification_helpers.add_commenter_to_comment_notifications(toolkit.c.userobj.id, res['thread_id'], res['id'])

        h.redirect_to(
            helpers.get_redirect_url(
                content_type,
                content_item_id if content_type == 'datarequest' else c.pkg.name,
                'comment_' + str(res['id']) if success else ('comment_form' if comment_type == 'new' else 'reply_' + str(parent_id))
            ))

    return helpers.render_content_template(content_type)


def delete(content_type, content_item_id, comment_id):
    context = {'model': model, 'user': c.user}
    data_dict = {'id': content_item_id}

    # Auth check to make sure the user can see this content item
    helpers.check_content_access(content_type, context, data_dict)

    try:
        # Load the content item
        helpers.get_content_item(content_type, context, data_dict)
    except:
        abort(403)

    try:
        data_dict = {'id': comment_id, 'content_type': content_type, 'content_item_id': content_item_id}
        get_action('comment_delete')(context, data_dict)
    except Exception as e:
        log.debug(e)
        if e.error_dict and e.error_dict.get('message'):
            msg = e.error_dict['message']
        else:
            msg = str(e)
        h.flash_error(msg)

    h.redirect_to(
        helpers.get_redirect_url(
            content_type,
            content_item_id if content_type == 'datarequest' else c.pkg.name,
            'comment_' + str(comment_id)
        ))

    return helpers.render_content_template(content_type)


def flag(comment_id):
    if authz.auth_is_loggedin_user():
        # Using the comment model rather than the update action because update action updates modified timestamp
        comment = comment_model.Comment.get(comment_id)
        if comment and not comment.flagged:
            comment.flagged = True
            model.Session.add(comment)
            model.Session.commit()
            email_notifications.flagged_comment_notification(comment)


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
            or not authz.auth_is_loggedin_user() \
            or not helpers.user_can_manage_comments(content_type, content_item_id):
        abort(403)

    comment.flagged = False

    model.Session.add(comment)
    model.Session.commit()

    h.flash_success(_('Comment un-flagged'))

    data_dict = {'id': content_item_id}

    if content_type == 'datarequest':
        c.datarequest = get_action('show_datarequest')(context, data_dict)
        h.redirect_to(str('/datarequest/comment/%s#comment_%s' % (content_item_id, comment_id)))
    else:
        c.pkg_dict = get_action('package_show')(context, data_dict)
        c.pkg = context['package']
        h.redirect_to(str('/dataset/%s#comment_%s' % (content_item_id, comment_id)))

    return helpers.render_content_template(content_type)


def dataset_comments(dataset_id):
    context = {'model': model, 'user': c.user}

    data_dict = {'id': dataset_id}
    content_type = 'dataset'
    # Auth check to make sure the user can see this content item
    helpers.check_content_access(content_type, context, data_dict)

    try:
        # Load the content item
        helpers.get_content_item(content_type, context, data_dict)
    except:
        abort(403)
    return toolkit.render('package/comments.html')