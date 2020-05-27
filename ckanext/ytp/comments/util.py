from lxml.html.clean import Cleaner, autolink_html
from lxml.html import fromstring
from ckan import logic
import logging

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
    except Exception, e:
        if type(e).__name__ == "ParserError":
            raise logic.ValidationError("Comment text is required")
        else:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            log.debug(message)

def convert_html_to_text(text):
    try:
        # Returns the text content of the element, including the text content of its children, with no markup.
        return fromstring(text.replace('<br/>', '\n')).text_content()
    except Exception, e:
        if type(e).__name__ == "ParserError":
            raise logic.ValidationError("Text is required")
        else:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            log.debug(message)