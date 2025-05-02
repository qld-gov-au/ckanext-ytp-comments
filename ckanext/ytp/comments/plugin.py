# encoding: utf-8

import logging

from ckan import model, plugins
from ckan.plugins import implements, toolkit

from ckanext.ytp.comments.model import CommentThread, Comment, COMMENT_APPROVED

from . import helpers, notification_helpers, util
from .plugin_mixins.flask_plugin import MixinPlugin

log = logging.getLogger(__name__)

unicode_safe = toolkit.get_validator('unicode_safe')


class YtpCommentsPlugin(MixinPlugin, plugins.SingletonPlugin):
    implements(plugins.IConfigurer, inherit=True)
    implements(plugins.IPackageController, inherit=True)
    implements(plugins.ITemplateHelpers, inherit=True)
    implements(plugins.IActions, inherit=True)
    implements(plugins.IAuthFunctions, inherit=True)

    # IConfigurer

    def configure(self, config):
        log.debug("Configuring comments module")

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('public/javascript/', 'comments_js')

    def update_config_schema(self, schema):
        schema.update({
            'ckan.comments.profanity_list': [
                toolkit.get_validator('ignore_missing'),
                unicode_safe
            ],
        })

        return schema

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'get_comment_thread': helpers.get_comment_thread,
            'get_content_type_comments_badge': helpers.get_content_type_comments_badge,
            'threaded_comments_enabled': helpers.threaded_comments_enabled,
            'users_can_edit': helpers.users_can_edit,
            'user_can_edit_comment': helpers.user_can_edit_comment,
            'user_can_manage_comments': helpers.user_can_manage_comments,
            'get_org_id': helpers.get_org_id,
            'user_comment_follow_mute_status': notification_helpers.get_user_comment_follow_mute_status,
            'ytp_comments_show_comments_tab_page': helpers.show_comments_tab_page,
            'ytp_comments_notification_recipients_enabled':
                helpers.get_comment_notification_recipients_enabled,
            'ytp_comments_unreplied_comments_x_days': helpers.unreplied_comments_x_days,
        }

    # IActions

    def get_actions(self):
        from ckanext.ytp.comments.logic.action import get, create, delete, update

        return {
            "comment_create": create.comment_create,
            "thread_show": get.thread_show,
            "comment_update": update.comment_update,
            "comment_show": get.comment_show,
            "comment_delete": delete.comment_delete,
            "comment_count": get.comment_count
        }

    # IAuthFunctions

    def get_auth_functions(self):
        from ckanext.ytp.comments.logic.auth import get, create, delete, update

        return {
            'comment_create': create.comment_create,
            'comment_update': update.comment_update,
            'comment_show': get.comment_show,
            'comment_delete': delete.comment_delete,
            "comment_count": get.comment_count
        }

    # IPackageController

    # CKAN < 2.10

    def before_view(self, pkg_dict):
        return self.before_dataset_view(pkg_dict)

    def before_index(self, pkg_dict):
        return self.before_dataset_index(pkg_dict)

    # CKAN 2.10

    def before_dataset_view(self, pkg_dict):
        # TODO: append comments from model to pkg_dict
        return pkg_dict

    def before_dataset_index(self, pkg_dict):
        """Index dataset comments to make them searchable via package_search"""
        thread = self._get_comment_thread(pkg_dict["name"], pkg_dict["type"])

        if thread:
            pkg_dict["extras_ytp_comments_idx"] = util.get_comments_data_for_index(thread)

        return pkg_dict

    def _get_comment_thread(self, content_id, content_type):
        """Get a comment thread if exists and attach related comments to it,
        otherwise return None"""
        thread_url = "/{}/{}".format(content_type, content_id)
        thread = model.Session.query(CommentThread) \
            .filter(CommentThread.url == thread_url) \
            .first()

        if not thread:
            return

        comments = model.Session.query(Comment). \
            filter(Comment.thread_id == thread.id). \
            filter(Comment.state == 'active'). \
            filter(Comment.approval_status == COMMENT_APPROVED)

        thread_dict = thread.as_dict()
        thread_dict["comments"] = [
            c.as_dict(only_active_children=False) for c in comments.all()
        ]

        return thread_dict
