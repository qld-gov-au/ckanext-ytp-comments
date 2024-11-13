# encoding: utf-8

import logging
import re
from lxml.html.clean import Cleaner, autolink_html
from lxml.html import fromstring
from bs4 import BeautifulSoup
from ckan.plugins.toolkit import ValidationError

log = logging.getLogger(__name__)


ALLOWED_TAGS = [
    "em", "strong", "cite", "code", "ul", "ol", "li", "p", "blockquote"
]


def clean_input(comment):
    try:
        data = comment
        if 'href' not in data:
            data = autolink_html(data, avoid_elements=['a'])

        cleaner = Cleaner(add_nofollow=True, allow_tags=ALLOWED_TAGS,
                          remove_unknown_tags=False)
        content = cleaner.clean_html(data).replace('\n', '<br/>')
        return content
    except Exception as e:
        if type(e).__name__ == "ParserError":
            raise ValidationError("Comment text is required")
        else:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            log.debug(message)


def remove_HTML_markup(text):
    try:
        # Returns the text content of the element, including the text content of its children, with no HTML markup.
        return fromstring(text.replace('<br/>', '\n')).text_content()
    except Exception as e:
        if type(e).__name__ == "ParserError":
            raise ValidationError("Text is required")
        else:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            log.debug(message)


def get_comments_data_for_index(thread):
    chunks = []

    for comment in thread["comments"]:
        if comment["state"] != "active":
            continue

        content = comment.get("content") or ""
        if content:
            content = strip_html_tags(content)
        chunks.append(content)
        chunks.append(comment.get("subject") or "")

    return _munge_to_string(set(chunks))


def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")

    return re.sub("\r", " ", soup.get_text()).strip()


def _munge_to_string(chunks):
    unique_words = set()

    for chunk in chunks:
        words = chunk.split()
        unique_words.update(words)

    return " ".join(unique_words)
