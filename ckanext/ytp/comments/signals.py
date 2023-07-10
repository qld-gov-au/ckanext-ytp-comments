import logging

log = logging.getLogger(__name__)

try:
    import ckan.plugins.toolkit as tk

    ckanext = tk.signals.ckanext

    created = ckanext.signal("comments:created")
    """Sent when a new comment created.
    Params:
        sender: Thread ID
        comment: comment dictionary
    """

    updated = ckanext.signal("comments:updated")
    """Sent after an update of exisning comment.
    Params:
        sender: Thread ID
        comment: comment dictionary
    """

    deleted = ckanext.signal("comments:deleted")
    """Sent when a comment is deleted.
    Params:
        sender: Thread ID
        comment: comment dictionary
    """

except AttributeError:
    log.info("YTP-Comments: Signals only available in CKAN 2.10+")
