# encoding: utf-8

import ckan.plugins as p

from ckanext.ytp.comments import helpers


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes

    def before_map(self, map):
        """
            /dataset/NAME/comments/reply/PARENT_ID
            /dataset/NAME/comments/add
        """
        controller = 'ckanext.ytp.comments.controllers.pylons_controllers:CommentController'
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
        notification_controller = 'ckanext.ytp.comments.controllers.pylons_controllers:NotificationController'
        map.connect('/comments/{thread_or_comment_id}/follow', controller=notification_controller, action='follow')
        map.connect('/comments/{thread_or_comment_id}/mute', controller=notification_controller, action='mute')
        return map
