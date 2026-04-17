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
    When the user logs in with username "standard_user" and password "secret_sauce"
    Then the user should land on the products page

  # Scenario Outline: one scenario, many data rows — keeps the feature DRY
  # Each Examples row generates a separate test case in the report
  # @regression
  # Scenario Outline: Login failure — <scenario>
  #   When the user logs in with username "<username>" and password "<password>"
  #   Then the login error message should be displayed
  #   # And there are "zero" items in the "bathroom" section

  #   Examples: Invalid credential combinations
  #     | scenario          | username      | password      |
  #     | invalid username  | wrong_user    | secret_sauce  |
  #     | invalid password  | standard_user | wrong_pass    |
