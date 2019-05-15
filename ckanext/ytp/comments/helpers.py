import ckan.plugins.toolkit as toolkit
import re

from ckan.common import config, request
from profanity import profanity


def threaded_comments_enabled():
    return toolkit.asbool(config.get('ckan.comments.threaded_comments', False))


def users_can_edit():
    return toolkit.asbool(config.get('ckan.comments.users_can_edit', False))


def profanity_check(cleaned_comment):
    profanity.load_words(load_bad_words())
    return profanity.contains_profanity(cleaned_comment)


def load_bad_words():
    filepath = config.get('ckan.comments.bad_words_file', None)
    if not filepath:
        # @todo: dynamically set this path
        filepath = '/usr/lib/ckan/default/src/ckanext-ytp-comments/ckanext/ytp/comments/bad_words.txt'

    f = open(filepath, 'r')
    x = f.read().splitlines()
    f.close()
    return x
