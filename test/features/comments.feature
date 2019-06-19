@smoke
Feature: Comments

    Scenario: DQL-74 BDD-1a Dataset comment submission access (non-logged in user)
        Given "Unathenticated" as the persona
        Then I go to dataset "warandpeace"
        Then I should see an element with xpath "//a[contains(string(), 'Login to comment')]"
        And I should not see "Add a comment"

    Scenario: DQL-74 BDD-1b Dataset comment submission access (Logged in user)
        Given "CKANUser" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        Then I should see an element with xpath "//h3[contains(string(), 'Add a comment')]"
        Then I take a screenshot

    Scenario: DQL-74 BDD-2 Dataset comment submission (Logged in user)
        Given "CKANUser" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        Then I should see an element with xpath "//h3[contains(string(), 'Add a comment')]"
        Then I submit a comment with subject "Test subject" and comment "This is a test comment"
        Then I should see "This is a test comment" within 10 seconds

    Scenario: DQL-74 BDD-4 Data request profane comment submission (Logged in user)
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        Then I should see an element with xpath "//h3[contains(string(), 'Add a comment')]"
        Then I submit a comment with subject "Test subject" and comment "Go fuck yourself!"
        Then I should see "Comment blocked due to profanity" within 5 seconds
        Then I take a screenshot

    Scenario: DQL-74 BDD-3 Data request comment submission (Logged in user)
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        Then I should see an element with xpath "//h3[contains(string(), 'Add a comment')]"
        Then I submit a comment with subject "Test subject" and comment "This is a test comment"
        Then I should see "This is a test comment" within 10 seconds

    Scenario: DQL-74 BDD-5 Report profane comment (Logged in user)
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        And I press the element with xpath "//a[contains(string(), 'Report')]"
        Then I should see "Reported" within 5 seconds
        Then I take a screenshot
        # @Todo: Need to check email notifications sent

    Scenario: DQL-74 BDD-6 Reply to comment (Logged in user)
        Given "CKANUser" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        Then I submit a reply with comment "This is a reply"
        Then I should see "This is a reply" within 10 seconds

    Scenario: DQL-74 BDD-7a Admin user delete comment
        Given "SalsaAdmin" as the persona
        When I log in
        Then I go to dataset "warandpeace"
        And I press the element with xpath "//a[@title='Delete comment']"
        Then I should see "Are you sure you want to delete this comment?" within 1 seconds
        Then I press the element with xpath "//button[contains(string(), 'Confirm')]"
        Then I should see "This comment was deleted." within 2 seconds
        Then I take a screenshot

    Scenario: DQL-74 BDD-7b Sysadmin user delete comment
        Given "Admin" as the persona
        When I log in
        And I go to data request "Test Request" comments
        And I press the element with xpath "//a[@title='Delete comment']"
        Then I should see "Are you sure you want to delete this comment?" within 1 seconds
        Then I press the element with xpath "//button[contains(string(), 'Confirm')]"
        Then I should see "This comment was deleted." within 2 seconds
        Then I take a screenshot
