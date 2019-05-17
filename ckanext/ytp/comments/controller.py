import ckan.authz as authz
import logging
import email_notifications
import ckan.plugins.toolkit as toolkit
import helpers

from ckan.lib.base import h, BaseController, render, abort, request
from ckan import model
from ckan.common import c, _
from ckan.logic import check_access, get_action, clean_dict, tuplize_dict, ValidationError, parse_params
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
            success = False
            try:
                res = get_action('comment_update')(context, data_dict)
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
            # if success:
            #     h.redirect_to(str('/dataset/%s#comment_%s' % (c.pkg.name, res['id'])))
            # else:
            #     # @todo check content_type for return URL
            #     print(content_type)
            #     h.redirect_to(str('/dataset/%s#edit_%s' % (c.pkg.name, comment_id)))

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
        '''
        Allows the user to add a comment to an existing dataset or datarequest
        :param comment_type:
        :param content_item_id:
        :param content_type:
        :return:
        '''
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
                email_notifications. notify_admins_and_commenters(
                    # @todo: refactor to helper function
                    c.datarequest['organization_id'] if ('dataset' if not vars().has_key('content_type') else content_type) == 'datarequest' else c.pkg.owner_org,
                    toolkit.c.userobj,
                    '/templates/email/notification-new-comment.txt',
                    'Queensland Government open data portal - New comment',
                    'dataset' if not vars().has_key('content_type') else content_type,
                    # c.pkg.name,
                    # @todo: refactor to helper function
                    c.datarequest['id'] if ('dataset' if not vars().has_key('content_type') else content_type) == 'datarequest' else c.pkg.name,
                    data_dict['url'],
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
            data_dict = {'id': comment_id}
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
            context = {'model': model, 'user': c.user}
            comment = get_action('comment_show')(context, {'id': comment_id})
            if comment and not comment['flagged']:
                comment['comment'] = comment['content']
                comment['flagged'] = True
                get_action('comment_update')(context, comment)

    def unflag(self, dataset_id, comment_id):
        if not authz.auth_is_loggedin_user():
            abort(403)

        context = {'model': model, 'user': c.user}
        comment = get_action('comment_show')(context, {'id': comment_id})

        if not comment or not comment['flagged']:
            abort(403)

        if not check_access('package_update', context, {"id": dataset_id}):
            abort(403)

        c.pkg_dict = get_action('package_show')(context, {'id': dataset_id})
        c.pkg = context['package']
        comment['comment'] = comment['content']
        comment['flagged'] = False
        get_action('comment_update')(context, comment)
        h.flash_success(_('Comment un-flagged'))
        h.redirect_to(str('/dataset/%s' % c.pkg.name))

        return render("package/read.html")
