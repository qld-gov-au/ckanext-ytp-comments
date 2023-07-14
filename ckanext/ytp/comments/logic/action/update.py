# encoding: utf-8

import datetime
import logging

from ckan.plugins.toolkit import abort, asbool, check_access, config, get_or_bust, \
    ValidationError

from ckanext.ytp.comments import helpers, model as comment_model, util
from . import _trigger_package_index_on_comment

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

    _trigger_package_index_on_comment(comment.thread_id)

    return comment.as_dict()
