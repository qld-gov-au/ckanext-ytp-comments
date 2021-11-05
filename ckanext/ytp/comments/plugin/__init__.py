# encoding: utf-8

import logging

from ckan import plugins
from ckan.plugins import implements, toolkit

from ckanext.ytp.comments import helpers, notification_helpers

log = logging.getLogger(__name__)


if toolkit.check_ckan_version("2.9"):
    from ckanext.ytp.comments.plugin.flask_plugin import MixinPlugin
else:
    from ckanext.ytp.comments.plugin.pylons_plugin import MixinPlugin


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
                unicode
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
            'ytp_comments_show_comments_tab_page': helpers.show_comments_tab_page
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

    def before_view(self, pkg_dict):
        # TODO: append comments from model to pkg_dict
        return pkg_dict
