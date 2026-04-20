@sauce @login
Feature: SauceDemo User Authentication
  As a SauceDemo user
  I want to authenticate with my credentials
  So that I can access the product catalog
# Background runs before EVERY scenario in this feature — no need to repeat the Given step

  Background:
    Given the user is on the SauceDemo login page

  @smoke
  Scenario: Successful login with valid credentials
    When the user logs in with username standard_user and password secret_sauce
    Then the user should land on the products page
    # Then the user pays 5
    # Then the order total is 5
    Then I have five products
    And the submit button is disabled
    # Each Examples row generates a separate test case in the report

  @regression_sd
  Scenario Outline: Login failure — <scenario>
    When the user logs in with username <username> and password <password>
    Then the login error message should be displayed
    And there are <zero> items in the <bathroom> section

    Examples:    Invalid credential combinations
      | scenario         | username      | password     | items | bathroom |
      | invalid username | wrong_user    | secret_sauce | asd   | sda      |
      | invalid password | standard_user | wrong_pass   | asd   | asd      |
