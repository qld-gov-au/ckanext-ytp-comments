from behave import step
from behaving.personas.steps import *  # noqa: F401, F403
from behaving.mail.steps import *  # noqa: F401, F403
from behaving.web.steps import *  # noqa: F401, F403
from behaving.web.steps.url import when_i_visit_url
import email
import quopri
import six


@step(u'I get the current URL')
def get_current_url(context):
    context.browser.evaluate_script("document.documentElement.clientWidth")


@step(u'I go to homepage')
def go_to_home(context):
    when_i_visit_url(context, '/')


@step(u'I go to register page')
def go_to_register_page(context):
    context.execute_steps(u"""
        When I go to homepage
        And I click the link with text that contains "Register"
    """)


@step(u'I log in')
def log_in(context):
    assert context.persona
    context.execute_steps(u"""
        When I go to homepage
        And I resize the browser to 1024x2048
        And I click the link with text that contains "Log in"
        And I log in directly
    """)


@step(u'I log in directly')
def log_in_directly(context):
    """
    This differs to the `log_in` function above by logging in directly to a page where the user login form is presented
    :param context:
    :return:
    """

    assert context.persona
    context.execute_steps(u"""
        When I attempt to log in with password "$password"
        Then I should see an element with xpath "//a[@title='Log out']"
    """)


@step(u'I attempt to log in with password "{password}"')
def attempt_login(context, password):
    assert context.persona
    context.execute_steps(u"""
        When I fill in "login" with "$name"
        And I fill in "password" with "{}"
        And I press the element with xpath "//button[contains(string(), 'Login')]"
    """.format(password))


@step(u'I go to dataset page')
def go_to_dataset_page(context):
    when_i_visit_url(context, '/dataset')


@step(u'I go to dataset "{name}"')
def go_to_dataset(context, name):
    when_i_visit_url(context, '/dataset/' + name)


@step(u'I should receive a base64 email at "{address}" containing "{text}"')
def should_receive_base64_email_containing_text(context, address, text):
    should_receive_base64_email_containing_texts(context, address, text, None)


@step(u'I should receive a base64 email at "{address}" containing both "{text}" and "{text2}"')
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
        if six.PY2:
            decoded_payload = payload_bytes.decode('base64')
        else:
            import base64
            decoded_payload = six.ensure_text(base64.b64decode(six.ensure_binary(payload_bytes)))
        print('decoded_payload: ', decoded_payload)
        return text in decoded_payload and (not text2 or text2 in decoded_payload)

    assert context.mail.user_messages(address, filter_contents)


# ckanext-ytp-comments


@step(u'I go to dataset "{name}" comments')
def go_to_dataset_comments(context, name):
    context.execute_steps(u"""
        When I go to dataset "%s"
        And I click the link with text that contains "Comments"
    """ % (name))


@step(u'I should see the add comment form')
def comment_form_visible(context):
    context.execute_steps(u"""
        Then I should see an element with xpath "//textarea[@name='comment']"
    """)


@step(u'I should not see the add comment form')
def comment_form_not_visible(context):
    context.execute_steps(u"""
        Then I should not see an element with xpath "//input[@name='subject']"
        And I should not see an element with xpath "//textarea[@name='comment']"
    """)


@step(u'I go to organisation page')
def go_to_organisation_page(context):
    when_i_visit_url(context, '/organization')


@step(u'I set persona var "{key}" to "{value}"')
def set_persona_var(context, key, value):
    context.persona[key] = value


@step(u'I submit a comment with subject "{subject}" and comment "{comment}"')
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


@step(u'I submit a reply with comment "{comment}"')
def submit_reply_with_comment(context, comment):
    """
    There can be multiple comment forms per page (add, edit, reply) each with fields named "subject" and "comment"
    This step overcomes a limitation of the fill() method which only fills a form field by name
    :param context:
    :param comment:
    :return:
    """
    context.execute_steps(u'Then I click the link with text that contains "Reply"')
    context.browser.execute_script("""
        document.querySelector('.comment-wrapper form.comment-reply textarea[name="comment"]').value = '%s';
        """ % comment)
    context.execute_steps(u'Then I take a screenshot')
    context.browser.execute_script("""
        document.querySelector('.comment-wrapper form.comment-reply .btn-primary[type="submit"]').click();
        """)
