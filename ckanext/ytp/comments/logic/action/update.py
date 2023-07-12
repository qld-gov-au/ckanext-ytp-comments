# encoding: utf-8

import datetime
import logging

from ckan.plugins.toolkit import abort, asbool, check_access, check_ckan_version, config, get_or_bust, \
    ValidationError

import ckanext.ytp.comments.model as comment_model
import ckanext.ytp.comments.util as util

from ckanext.ytp.comments import helpers

log = logging.getLogger(__name__)


def comment_update(context, data_dict):
    model = context['model']

    check_access("comment_update", context, data_dict)

    cid = get_or_bust(data_dict, 'id')
    comment = comment_model.Comment.get(cid)
    if not comment:
        return abort(404)

    # Validate that we have the required fields.
    if not all([data_dict.get('comment')]):
        raise ValidationError("Comment text is required")

    # Cleanup the comment
    cleaned_comment = util.clean_input(data_dict.get('comment'))

    # Run profanity check
    if asbool(config.get('ckan.comments.check_for_profanity', False)) \
            and (helpers.profanity_check(cleaned_comment) or helpers.profanity_check(data_dict.get('subject', ''))):
        raise ValidationError("Comment blocked due to profanity.")

    comment.subject = data_dict.get('subject')
    comment.comment = cleaned_comment
    comment.modified_date = datetime.datetime.utcnow()

    comment.flagged = data_dict.get('flagged')

    model.Session.add(comment)
    model.Session.commit()

    comment_dict = comment.as_dict()
    if check_ckan_version('2.10'):
        thread_id = comment_dict["thread_id"]
        log.debug("Notifying subscribers of comment update on thread [%s]", thread_id)
        from ckanext.ytp.comments import signals
        signals.updated.send(thread_id, comment=comment_dict)

    return comment_dict
