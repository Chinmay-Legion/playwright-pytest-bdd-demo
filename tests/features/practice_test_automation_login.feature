@pta @login
Feature: Practice Test Automation login
  As a registered user
  I want to log in to the practice site
  So that I can verify my credentials work correctly

  Background:
    Given the user is on the PTA login page

  @smoke @smoke_pta
  Scenario: Successful login with valid credentials
    When the user logs in with username "student" and password "Password123"
    Then the user should land on the login successful page

  @negative
  Scenario Outline: Login failure - <error_type>
    When the user logs in with username "<username>" and password "<password>"
    Then the error message should read "<expected_error>"

    Examples: Credential error scenarios
      | error_type       | username  | password    | expected_error            |
      | invalid username | wrongUser | Password123 | Your username is invalid! |
      | invalid password | student   | WrongPass   | Your password is invalid! |
