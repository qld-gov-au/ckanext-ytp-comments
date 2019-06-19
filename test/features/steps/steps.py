from behave import when
from behaving.web.steps import *  # noqa: F401, F403
from behaving.personas.steps import *  # noqa: F401, F403
from behaving.web.steps.url import when_i_visit_url


@when('I go to homepage')
def go_to_home(context):
    when_i_visit_url(context, '/')


@when('I log in')
def log_in(context):

    assert context.persona
    context.execute_steps(u"""
        When I go to homepage
        And I click the link with text that contains "Log in"
        And I fill in "login" with "$name"
        And I fill in "password" with "$password"
        And I press the element with xpath "//button[contains(string(), 'Login')]"
        Then I should see an element with xpath "//a[contains(string(), 'Log out')]"
    """)


@step(u'I go to dataset "{name}"')
def go_to_dataset(context, name):
    when_i_visit_url(context, '/dataset/' + name)


@step(u'I go to the data requests page')
def go_to_data_requests_page(context):
    when_i_visit_url(context, '/datarequest')


@step(u'I go to data request "{subject}"')
def go_to_data_request(context, subject):
    context.execute_steps(u"""
        When I go to the data requests page
        And I click the link with text "%s"
        Then I should see "%s" within 5 seconds
    """ % (subject, subject))


@step(u'I go to data request "{subject}" comments')
def go_to_data_request_comments(context, subject):
    context.execute_steps(u"""
        When I go to data request "%s"
        And I click the link with text that contains "Comments"
    """ % (subject))


@step(u'I submit a comment with subject "{subject}" and comment "{comment}"')
def submit_comment_with_subject_and_comment(context, subject, comment):

    assert context.persona
    context.execute_steps(u"""
        When I fill in "subject" with "%s"
        And I fill in "comment" with "%s"
        # Save is an input submit button without "name" or "id".
        And I press the element with xpath "//div/article/div/form[last()]/div/input[@value='Save']"
    """ % (subject, comment))


@step(u'I get the current URL')
def get_current_url(context):
    context.browser.evaluate_script("document.documentElement.clientWidth")


@step(u'I set persona var "{key}" to "{value}"')
def set_persona_var(context, key, value):
    context.persona[key] = value