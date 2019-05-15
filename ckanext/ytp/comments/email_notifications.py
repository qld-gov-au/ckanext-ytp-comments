import ckan.authz as authz
import ckan.lib.mailer as mailer
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import logging
import sqlalchemy

from ckan.common import config
from ckanext.ytp.comments.model import Comment, CommentThread


log1 = logging.getLogger(__name__)
NotFound = logic.NotFound
_and_ = sqlalchemy.and_


def load_notification_template(template):
    import os

    path = os.path.dirname(os.path.realpath(__file__)) + template

    try:
        fp = open(path, 'rb')
        notification_template = fp.read()
        fp.close()

        return notification_template
    except IOError as error:
        log1.error(error)
        raise


def mail_merge(msg, dict):

    if 'organization' in dict:
        msg = msg.replace('[[ORGANIZATION]]', dict['organization'])

    if 'user' in dict:
        msg = msg.replace('[[USER]]', dict['user'])

    if 'url' in dict:
        msg = msg.replace('[[URL]]', dict['url'])

    if 'email' in dict:
        msg = msg.replace('[[EMAIL]]', dict['email'])

    if 'name' in dict:
        msg = msg.replace('[[NAME]]', dict['name'])

    if 'comment_id' in dict:
        msg = msg.replace('[[COMMENT_ID]]', dict['comment_id'])

    return msg


def get_member_list(context, data_dict=None):
    '''
    :param id: the id or name of the group
    :type id: string
    :param object_type: restrict the members returned to those of a given type,
      e.g. ``'user'`` or ``'package'`` (optional, default: ``None``)
    :type object_type: string
    :param capacity: restrict the members returned to those with a given
      capacity, e.g. ``'member'``, ``'editor'``, ``'admin'``, ``'public'``,
      ``'private'`` (optional, default: ``None``)
    :type capacity: string

    :rtype: list of (id, type, capacity) tuples

    :raises: :class:`ckan.logic.NotFound`: if the group doesn't exist

    '''
    model = context['model']

    group = model.Group.get(logic.get_or_bust(data_dict, 'id'))
    if not group:
        raise NotFound

    obj_type = data_dict.get('object_type', None)
    capacity = data_dict.get('capacity', None)

    q = model.Session.query(model.Member).\
        filter(model.Member.group_id == group.id).\
        filter(model.Member.state == "active")

    if obj_type:
        q = q.filter(model.Member.table_name == obj_type)
    if capacity:
        q = q.filter(model.Member.capacity == capacity)

    trans = authz.roles_trans()

    def translated_capacity(capacity):
        try:
            return trans[capacity]
        except KeyError:
            return capacity

    return [(m.table_id, m.table_name, translated_capacity(m.capacity))
            for m in q.all()]


def get_admin_users_for_org(owner_org, excluded_emails=[]):
    '''
    A list of admin user emails for the supplied organisation ID
    :param owner_org: string
    :param excluded_emails: list
    :return:
    '''
    admin_users = []

    member_list = get_member_list(
        {'model': model},
        {
            'id': owner_org,
            'object_type': 'user',
            'capacity': 'admin'
        })

    for member in member_list:
        user = model.User.get(member[0])
        if user and user.email and user.email not in excluded_emails:
            admin_users.append(user.email)

    return admin_users


def send_notification_email(to, subject, msg):
    '''
    Use CKAN mailer logic to send an email to an individual email address
    :param to: string
    :param subject: string
    :param msg: string
    :return:
    '''
    # Attempt to send mail.
    mail_dict = {
        'recipient_email': to,
        'recipient_name': to,
        'subject': subject,
        'body': msg,
        'headers': {'reply-to': config.get('smtp.mail_from')}
    }

    try:
        mailer.mail_recipient(**mail_dict)
    except mailer.MailerException:
        log1.error(u'Cannot send email notification to %s.', to, exc_info=1)


def notify_admin_users(owner_org, template, subject, package_name, comment_id):
    admin_users = get_admin_users_for_org(owner_org)

    if admin_users:
        msg = load_notification_template(template)

        msg = mail_merge(msg, {
            'url': toolkit.url_for('dataset_read', id=package_name, qualified=True),
            'comment_id': comment_id
        })

        for user in admin_users:
            send_notification_email(
                user,
                subject,
                msg
            )


def notify_admins_and_commenters(owner_org, user, template, subject, content_type, content_item_id, thread_url, comment_id):
    '''

    :param owner_org: organization.id of the content item owner
    :param user: c.user_obj of the user who submitted the comment
    :param template: string indicating which email template to use
    :param subject: string to be used for email subject
    :param content_item_name:
    :param thread_url: URL of the comment thread (used to determine other commenters in thread)
    :param comment_id: ID of the comment submitted (used in URL of email body)
    :return:
    '''
    # Get all the org admin users (excluding the user who made the comment)
    admin_users = get_admin_users_for_org(owner_org, [user.email])

    # Get all the other commenters (excluding the user who made the comment)
    other_commenters = get_other_commenters(thread_url, user.email)

    # Combine the two lists
    users = list(set(admin_users + other_commenters))

    if users:
        msg = load_notification_template(template)
        msg = mail_merge(msg, {
            'url': get_content_item_link(content_type, content_item_id, comment_id)
        })

        for user in users:
            send_notification_email(
                user,
                subject,
                msg
            )


def get_other_commenters(thread_url, commenter_email):
    '''
    Queries the database to find other commenters for a given thread
    :param thread_url: URL of the comment thread
    :param commenter_email: Email address of the user who submitted the comment
    :return:
    '''
    session = model.Session

    comments = (
        session.query(
            model.User.email
        )
        .join(
            Comment,
            Comment.user_id==model.User.id
        )
        .join(
            CommentThread,
            Comment.thread_id==CommentThread.id
        )
        .filter(
            _and_(
                CommentThread.url == thread_url,
                model.User.email != commenter_email,
            ))
        .group_by(model.User.email)
    )

    return [email[0] for email in comments.all()]


def get_content_item_link(content_type, content_item_id, comment_id=None):
    '''
    Get a fully qualified URL to the content item being commented on.
    :param content_type: string Currently only supports 'dataset' or 'datarequest'
    :param content_item_id: string Package name, or Data Request ID
    :param comment_id: string `comment`.`id`
    :return:
    '''
    url = ''
    if content_type == 'datarequest':
        url = toolkit.url_for('datarequest_comment', id=content_item_id, qualified=True)
    else:
        url = toolkit.url_for('dataset_read', id=content_item_id, qualified=True)
    if comment_id:
        url += '#comment_' + str(comment_id)
    return url
