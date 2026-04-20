@pta @login
Feature: PracticeTestAutomation Login
  As a registered user
  I want to log in to the practice site
  So that I can verify my credentials work correctly

  Background:
    Given the user is on the PTA login page
    # And I have 5 products

  @pta
  Scenario: Successful login with valid credentials
    When the user logs in with username student and password Password123
    Then the user should land on the login successful page
    Then the submit button is enabled
    # Then the editor is not in the washroom
    # Then the user presses on the "button"
    # And the user is not in his right mind


    # And I have 6 products

  # The expected_error column drives the assertion — one step replaces two separate Then steps
  @regression_pta
  Scenario Outline: Login failure — <error_type>
    When the user logs in with username <username> and password <password>
    Then the error message should read "<expected_error>"

    Examples: Credential error scenarios
      | error_type       | username  | password     | expected_error            |
      | invalid username | wrongUser | Password123  | Your username is invalid! |
      | invalid password | student   | WrongPass    | Your password is invalid! |
