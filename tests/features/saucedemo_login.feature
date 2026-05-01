@sauce @login
Feature: SauceDemo user authentication
  As a SauceDemo user
  I want to authenticate with my credentials
  So that I can access the product catalog

  Background:
    Given the user is on the SauceDemo login page

  @smoke
  Scenario: Successful login with valid credentials
    When the user logs in with username "standard_user" and password "secret_sauce"
    Then the user should land on the products page

  @negative
  Scenario Outline: Login failure - <scenario>
    When the user logs in with username "<username>" and password "<password>"
    Then the login error message should be displayed

    Examples: Invalid credential combinations
      | scenario         | username      | password     |
      | invalid username | wrong_user    | secret_sauce |
      | invalid password | standard_user | wrong_pass   |
