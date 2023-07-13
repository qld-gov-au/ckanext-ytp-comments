import logging

import ckan.plugins.toolkit as tk
import ckan.lib.search as search

from ckanext.ytp.comments import signals, model as ytp_model

log = logging.getLogger(__name__)

'''This is a CKAN 2.10+ module'''


@signals.deleted.connect
def after_comment_delete(thread_id, comment):
    _trigger_package_index_on_comment(thread_id)


@signals.created.connect
def after_comment_created(thread_id, comment):
    _trigger_package_index_on_comment(thread_id)


@signals.updated.connect
def after_comment_updated(thread_id, comment):
    _trigger_package_index_on_comment(thread_id)


def _trigger_package_index_on_comment(thread_id):
    """We want to search by comment title/content, so we have to trigger
    a package index each time, when we are creating/updating/deleting the comment.
    Then, in the before_index we are going to index mentioned info along with the
    package metadata"""
    thread = ytp_model.CommentThread.get(thread_id)

    content_type, entity_id = _parse_thread_content(thread)

    if content_type == "datarequest":
        return

    try:
        package = tk.get_action("package_show")({"ignore_auth": True}, {"id": entity_id})
    except tk.ObjectNotFound:
        log.warn("Could not find package [%s] for comment thread [%s]!", entity_id, thread_id)
        return

    log.debug("Adding package [%s] comments to search index", package)
    index = search.PackageSearchIndex()
    index.update_dict(package)


def _parse_thread_content(thread):
    """
    Parse a thread url field to content_type and id
    e.g. /datarequest/0c9bfd23-49d0-47ce-ad2b-6195519dfa5e
         /dataset/df8e9120-ebeb-4945-abda-eb3df8c7b61b
         /dataset/test-ds-1
    """
    return thread.url.strip("/").split("/")