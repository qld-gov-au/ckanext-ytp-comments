import ckan.plugins as plugins
import ckan.model as model
from ckan.logic import get_action
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

    def get_helpers(self):
        return {
            'get_comment_thread': self._get_comment_thread,
            'get_comment_count_for_dataset': self._get_comment_count_for_dataset,
            'threaded_comments_enabled': helpers.threaded_comments_enabled,
            'users_can_edit': helpers.users_can_edit,
            'user_can_edit_comment': helpers.user_can_edit_comment,
            'user_can_manage_comments': helpers.user_can_manage_comments,
            'get_org_id': helpers.get_org_id,
            'user_comment_follow_mute_status': notification_helpers.get_user_comment_follow_mute_status
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

    def _get_comment_thread(self, dataset_name, content_type='dataset'):
        url = '/%s/%s' % (content_type, dataset_name)
        return get_action('thread_show')({'model': model, 'with_deleted': True}, {'url': url})

    def _get_comment_count_for_dataset(self, dataset_name, content_type='dataset'):
        url = '/%s/%s' % (content_type, dataset_name)
        count = get_action('comment_count')({'model': model}, {'url': url})
        return count
