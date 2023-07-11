# encoding: utf-8

import datetime
import logging

from ckan.plugins.toolkit import asbool, check_access, check_ckan_version, config, ValidationError

from ckanext.ytp.comments import helpers, model as comment_model, util

log = logging.getLogger(__name__)


def comment_create(context, data_dict):
    model = context['model']
    user = context['user']

    userobj = model.User.get(user)

    check_access("comment_create", context, data_dict)

    # Validate that we have the required fields.
    if not all([data_dict.get('comment')]):
        raise ValidationError("Comment text is required")

    thread_id = data_dict.get('thread_id')

    if not thread_id:
        url = data_dict.get('url')
        if url:
            thread = comment_model.CommentThread.from_url(url)
            thread_id = thread.id if thread else None

    if not thread_id:
        raise ValidationError("Thread identifier or URL is required")

    # Cleanup the comment
    cleaned_comment = util.clean_input(data_dict.get('comment'))

    # Run profanity check
    if asbool(config.get('ckan.comments.check_for_profanity', False)) \
            and (helpers.profanity_check(cleaned_comment) or helpers.profanity_check(data_dict.get('subject', ''))):
        raise ValidationError({"message": "Comment blocked due to profanity."})

    # Create the object
    cmt = comment_model.Comment(thread_id=thread_id,
                                comment=cleaned_comment)
    cmt.user_id = userobj.id
    cmt.subject = data_dict.get('subject', 'No subject')

    if 'creation_date' in context:
        cmt.creation_date = datetime.datetime.fromtimestamp(context['creation_date'])

    # Check if there is a parent ID and that it is valid
    # TODO, validity in this case includes checking parent is not
    # deleted.
    prt = data_dict.get('parent_id')
    if prt:
        parent = comment_model.Comment.get(prt)
        if parent:
            cmt.parent_id = parent.id

    # approval and spam checking removed

    model.Session.add(cmt)
    model.Session.commit()

    comment_dict = cmt.as_dict()
    if check_ckan_version('2.10'):
        from ckanext.ytp.comments import signals
        signals.created.send(thread_id, comment=comment_dict)

    return comment_dict
