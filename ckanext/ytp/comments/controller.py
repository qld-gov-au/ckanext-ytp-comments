import ckan.authz as authz
import logging
import email_notifications
import ckan.plugins.toolkit as toolkit
import model as comment_model
import helpers

from ckan.lib.base import h, BaseController, abort, request
from ckan import model
from ckan.common import c, _
from ckan.logic import get_action, clean_dict, tuplize_dict, ValidationError, parse_params
from ckan.lib.navl.dictization_functions import unflatten


log = logging.getLogger(__name__)


class CommentController(BaseController):
    def add(self, dataset_id, content_type='dataset'):
        return self._add_or_reply('new', dataset_id, content_type)

    def edit(self, content_type, content_item_id, comment_id):

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
            except ValidationError, ve:
                log.debug(ve)
                if ve.error_dict and ve.error_dict.get('message'):
                    msg = ve.error_dict['message']
                else:
                    msg = str(ve)
                h.flash_error(msg)
            except Exception, e:
                log.debug(e)
                abort(403)

            h.redirect_to(
                helpers.get_redirect_url(
                    content_type,
                    content_item_id if content_type == 'datarequest' else c.pkg.name,
                    'comment_' + str(comment_id) if success else 'edit_' + str(comment_id)
                ))

        return helpers.render_content_template(content_type)

    def reply(self, content_type, dataset_id, parent_id):
        c.action = 'reply'

        try:
            data = {'id': parent_id}
            c.parent_dict = get_action("comment_show")({'model': model, 'user': c.user},
                                                       data)
            c.parent = data['comment']
        except:
            abort(404)

        return self._add_or_reply('reply', dataset_id, content_type, parent_id)

    def _add_or_reply(self, comment_type, content_item_id, content_type, parent_id=None):
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
            except ValidationError, ve:
                log.debug(ve)
                if ve.error_dict and ve.error_dict.get('message'):
                    msg = ve.error_dict['message']
                else:
                    msg = str(ve)
                h.flash_error(msg)
            except Exception, e:
                log.debug(e)
                abort(403)

            if success:
                if comment_type == 'reply':
                    email_notifications.notify_admins_and_other_commenters(
                        helpers.get_org_id(content_type),
                        toolkit.c.userobj,
                        'notification-new-comment',
                        content_type,
                        helpers.get_content_item_id(content_type),
                        res['parent_id'],
                        res['id']
                    )
                else:
                    email_notifications.notify_admins(
                        helpers.get_org_id(content_type),
                        toolkit.c.userobj,
                        'notification-new-comment',
                        content_type,
                        helpers.get_content_item_id(content_type),
                        res['id']
                    )

            h.redirect_to(
                helpers.get_redirect_url(
                    content_type,
                    content_item_id if content_type == 'datarequest' else c.pkg.name,
                    'comment_' + str(res['id']) if success else ('comment_form' if comment_type == 'new' else 'reply_' + str(parent_id))
                ))

        return helpers.render_content_template(content_type)

    def delete(self, content_type, content_item_id, comment_id):

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
        except Exception, e:
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

    def flag(self, comment_id):
        if authz.auth_is_loggedin_user():
            # Using the comment model rather than the update action because update action updates modified timestamp
            comment = comment_model.Comment.get(comment_id)
            if comment and not comment.flagged:
                comment.flagged = True
                model.Session.add(comment)
                model.Session.commit()
                email_notifications.flagged_comment_notification(comment)

    def unflag(self, content_type, content_item_id, comment_id):
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
