@comments
Feature: Comments

    Scenario: The Add Comment form should not display for a non-logged-in user - instead they see a 'Login to comment' button
        Given "Unathenticated" as the persona
        Then I go to dataset "warandpeace"
        Then I should see an element with xpath "//a[contains(string(), 'Login to comment')]"
        And I should not see "Add a comment"

    Scenario: Logged-in users see the add comment form
        Given "CKANUser" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        Then I should see an element with xpath "//h3[contains(string(), 'Add a comment')]"

    @comment-add
    Scenario: When a logged-in user submits a comment on a Dataset the comment should display within 10 seconds
        Given "CKANUser" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        Then I should see an element with xpath "//h3[contains(string(), 'Add a comment')]"
        Then I submit a comment with subject "Test subject" and comment "This is a test comment"
        Then I should see "This is a test comment" within 10 seconds

    @comment-profane
    Scenario: When a logged-in user submits a comment containing profanity on a Data Request they should receive an error message and the commment will not appear
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        Then I should see an element with xpath "//h3[contains(string(), 'Add a comment')]"
        Then I submit a comment with subject "Test subject" and comment "Go fuck yourself!"
        Then I should see "Comment blocked due to profanity" within 5 seconds

    @comment-add
    Scenario: When a logged-in user submits a comment on a Data Request the comment should then be visible on the Comments tab of the Data Request
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        Then I should see an element with xpath "//h3[contains(string(), 'Add a comment')]"
        Then I submit a comment with subject "Test subject" and comment "This is a test comment"
        Then I should see "This is a test comment" within 10 seconds

    @comment-report
    Scenario: When a logged-in user reports a comment on a Data Request the comment should be marked as reported and an email notification sent to the organisation admins
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        And I press the element with xpath "//a[contains(string(), 'Report')]"
        Then I should see "Reported" within 5 seconds
        When I wait for 3 seconds
        Then I should receive an email at "dr_admin@localhost" with subject "Queensland Government Open Data - Comments"

    @comment-report
    Scenario: When a logged-in user reports a comment on a Dataset the comment should be marked as reported and an email sent to the admins of the organisation
        Given "CKANUser" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        And I press the element with xpath "//a[contains(string(), 'Report')]"
        Then I should see "Reported" within 5 seconds
        When I wait for 3 seconds
        Then I should receive an email at "test_org_admin@localhost" with subject "Queensland Government Open Data - Comments"

    @comment-reply
    Scenario: When a logged-in user submits a reply comment on a Dataset, the comment should display within 10 seconds
        Given "CKANUser" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        Then I submit a reply with comment "This is a reply"
        Then I should see "This is a reply" within 10 seconds

    @comment-delete
    Scenario: When an Org Admin visits a dataset belonging to their organisation, they can delete a comment and the comment will be marked as deleted.
        Given "TestOrgAdmin" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        And I press the element with xpath "//a[@title='Delete comment']"
        Then I should see "Are you sure you want to delete this comment?" within 1 seconds
        Then I press the element with xpath "//button[contains(string(), 'Confirm')]"
        Then I should see "This comment was deleted." within 2 seconds

    @comment-delete
    Scenario: When an Org Admin visits a data request belonging to their organisation, they can delete a comment and the comment will be marked as deleted.
        Given "Admin" as the persona
        When I log in
        And I go to data request "Test Request" comments
        And I press the element with xpath "//a[@title='Delete comment']"
        Then I should see "Are you sure you want to delete this comment?" within 1 seconds
        Then I press the element with xpath "//button[contains(string(), 'Confirm')]"
        Then I should see "This comment was deleted." within 2 seconds
