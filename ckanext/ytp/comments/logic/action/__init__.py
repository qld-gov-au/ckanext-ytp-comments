# encoding: utf-8

import logging

from ckan.lib import search
import ckan.plugins.toolkit as tk

from ckanext.ytp.comments import model as ytp_model

log = logging.getLogger(__name__)


def _trigger_package_index_on_comment(thread_id):
    """We want to search by comment title/content, so we have to trigger
    a package index each time, when we are creating/updating/deleting the comment.
    Then, in the before_index we are going to index mentioned info along with the
    package metadata"""
    thread = ytp_model.CommentThread.get(thread_id)

    content_type, entity_id = thread.url.strip("/").split("/")

    if content_type == "datarequest":
        return

    try:
        package = tk.get_action("package_show")({"ignore_auth": True}, {"id": entity_id})
    except tk.ObjectNotFound:
        log.warning("Could not find package [%s] for comment thread [%s]!", entity_id, thread_id)
        return

    index = search.PackageSearchIndex()
    index.update_dict(package)
