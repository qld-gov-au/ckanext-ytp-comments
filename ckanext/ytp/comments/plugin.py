import ckan.plugins as plugins
from ckan.plugins import implements, toolkit

import helpers
import notification_helpers
import logging

log = logging.getLogger(__name__)


class YtpCommentsPlugin(plugins.SingletonPlugin):
    implements(plugins.IRoutes, inherit=True)
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

    # IRoutes

    def before_map(self, map):
        """
            /dataset/NAME/comments/reply/PARENT_ID
            /dataset/NAME/comments/add
        """
        controller = 'ckanext.ytp.comments.controller:CommentController'
        if helpers.show_comments_tab_page():
            map.connect('dataset_comments', '/dataset/{dataset_id}/comments', controller=controller, action='dataset_comments', ckan_icon='comment')
        map.connect('/dataset/{dataset_id}/comments/add', controller=controller, action='add')
        map.connect('/{content_type}/{dataset_id}/comments/add', controller=controller, action='add')
        map.connect('/{content_type}/{content_item_id}/comments/{comment_id}/edit', controller=controller, action='edit')
        map.connect('/{content_type}/{dataset_id}/comments/{parent_id}/reply', controller=controller, action='reply')
        map.connect('/{content_type}/{content_item_id}/comments/{comment_id}/delete', controller=controller, action='delete')
        # Flag a comment as inappropriate
        map.connect('/comment/{comment_id}/flag', controller=controller, action='flag')
        # Un-flag a comment as inappropriate
        map.connect('/{content_type}/{content_item_id}/comments/{comment_id}/unflag', controller=controller, action='unflag')
        # Routes for following and muting comment notifications
        notification_controller = 'ckanext.ytp.comments.notification_controller:NotificationController'
        map.connect('/comments/{thread_or_comment_id}/follow', controller=notification_controller, action='follow')
        map.connect('/comments/{thread_or_comment_id}/mute', controller=notification_controller, action='mute')
        return map
