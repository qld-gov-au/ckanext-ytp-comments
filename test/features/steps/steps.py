from behave import when, then
from behaving.personas.steps import *  # noqa: F401, F403
from behaving.mail.steps import *  # noqa: F401, F403
from behaving.web.steps import *  # noqa: F401, F403
import email
import quopri
import six


# Monkey-patch Selenium 3 to handle Python 3.9
import base64
if not hasattr(base64, 'encodestring'):
    base64.encodestring = base64.encodebytes


@when(u'I take a debugging screenshot')
def debug_screenshot(context):
    """ Take a screenshot only if debugging is enabled in the persona.
    """
    if context.persona and context.persona.get('debug') == 'True':
        context.execute_steps(u"""
            When I take a screenshot
        """)


@when(u'I go to homepage')
def go_to_home(context):
    context.execute_steps(u"""
        When I visit "/"
    """)


@when(u'I go to register page')
def go_to_register_page(context):
    context.execute_steps(u"""
        When I go to homepage
        And I press "Register"
    """)


@when(u'I log in')
def log_in(context):
    context.execute_steps(u"""
        When I go to homepage
        And I expand the browser height
        And I press "Log in"
        And I log in directly
    """)


@when(u'I expand the browser height')
def expand_height(context):
    # Work around x=null bug in Selenium set_window_size
    context.browser.driver.set_window_rect(x=0, y=0, width=1024, height=3072)


@when(u'I log in directly')
def log_in_directly(context):
    """
    This differs to the `log_in` function above by logging in directly to a page where the user login form is presented
    :param context:
    :return:
    """

    assert context.persona, "A persona is required to log in, found [{}] in context." \
        " Have you configured the personas in before_scenario?".format(context.persona)
    context.execute_steps(u"""
        When I attempt to log in with password "$password"
        Then I should see an element with xpath "//*[@title='Log out' or @data-bs-title='Log out']/i[contains(@class, 'fa-sign-out')]"
    """)


@when(u'I attempt to log in with password "{password}"')
def attempt_login(context, password):
    assert context.persona
    context.execute_steps(u"""
        When I fill in "login" with "$name"
        And I fill in "password" with "{}"
        And I press the element with xpath "//button[contains(string(), 'Login')]"
    """.format(password))


@when(u'I go to dataset page')
def go_to_dataset_page(context):
    context.execute_steps(u"""
        When I visit "/dataset"
    """)


@when(u'I go to dataset "{name}"')
def go_to_dataset(context, name):
    context.execute_steps(u"""
        When I visit "/dataset/{0}"
        And I take a debugging screenshot
    """.format(name))


@when(u'I go to organisation page')
def go_to_organisation_page(context):
    context.execute_steps(u"""
        When I visit "/organization"
    """)


@then(u'I should receive a base64 email at "{address}" containing "{text}"')
def should_receive_base64_email_containing_text(context, address, text):
    should_receive_base64_email_containing_texts(context, address, text, None)


@then(u'I should receive a base64 email at "{address}" containing both "{text}" and "{text2}"')
def should_receive_base64_email_containing_texts(context, address, text, text2):
    # The default behaving step does not convert base64 emails
    # Modified the default step to decode the payload from base64
    def filter_contents(mail):
        mail = email.message_from_string(mail)
        payload = mail.get_payload()
        payload += "=" * ((4 - len(payload) % 4) % 4)  # do fix the padding error issue
        payload_bytes = quopri.decodestring(payload)
        if len(payload_bytes) > 0:
            payload_bytes += b'='  # do fix the padding error issue
        decoded_payload = six.ensure_text(base64.b64decode(six.ensure_binary(payload_bytes)))
        print('Searching for', text, ' and ', text2, ' in decoded_payload: ', decoded_payload)
        return text in decoded_payload and (not text2 or text2 in decoded_payload)

    assert context.mail.user_messages(address, filter_contents)


# ckanext-ytp-comments


@when(u'I go to dataset "{name}" comments')
def go_to_dataset_comments(context, name):
    context.execute_steps(u"""
        When I go to dataset "%s"
        And I press "Comments"
    """ % (name))


@then(u'I should see the add comment form')
def comment_form_visible(context):
    context.execute_steps(u"""
        Then I should see an element with xpath "//textarea[@name='comment']"
    """)


@then(u'I should not see the add comment form')
def comment_form_not_visible(context):
    context.execute_steps(u"""
        Then I should not see an element with xpath "//input[@name='subject']"
        And I should not see an element with xpath "//textarea[@name='comment']"
    """)


@when(u'I submit a comment with subject "{subject}" and comment "{comment}"')
def submit_comment_with_subject_and_comment(context, subject, comment):
    """
    There can be multiple comment forms per page (add, edit, reply) each with fields named "subject" and "comment"
    This step overcomes a limitation of the fill() method which only fills a form field by name
    :param context:
    :param subject:
    :param comment:
    :return:
    """
    context.browser.execute_script("""
        subject_field = document.querySelector('form input[name="subject"]');
        if (subject_field) { subject_field.value = '%s'; }
        """ % subject)
    context.browser.execute_script("""
        form = document.querySelector('form#comment-add')
        if (!form) { form = document.querySelector('form#comment_form') }
        if (!form) { form = document.querySelector('form.dataset-form') }
        form.querySelector('textarea[name="comment"]').value = '%s';
        form.querySelector('.btn-primary[type="submit"]').click();
        """ % comment)


@when(u'I submit a reply with comment "{comment}"')
def submit_reply_with_comment(context, comment):
    """
    There can be multiple comment forms per page (add, edit, reply) each with fields named "subject" and "comment"
    This step overcomes a limitation of the fill() method which only fills a form field by name
    :param context:
    :param comment:
    :return:
    """
    context.execute_steps(u'When I click the link with text that contains "Reply"')
    context.browser.execute_script("""
        document.querySelector('.comment-wrapper form.comment-reply textarea[name="comment"]').value = '%s';
        """ % comment)
    context.execute_steps(u'When I take a screenshot')
    context.browser.execute_script("""
        document.querySelector('.comment-wrapper form.comment-reply .btn-primary[type="submit"]').click();
        """)
