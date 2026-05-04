@orangehrm @auth
Feature: OrangeHRM authentication
  As an HR administrator
  I want to sign in to OrangeHRM
  So that I can access protected HR modules

  @smoke
  Scenario: Administrator can login
    Given an OrangeHRM administrator exists
    When the user logs in to OrangeHRM
    Then the OrangeHRM dashboard should be displayed
    And the OrangeHRM user menu should be available

  @negative
  Scenario: Invalid credentials are rejected
    Given an OrangeHRM user has credentials:
      | username | password       |
      | Admin    | wrong-password |
    When the user attempts to login to OrangeHRM
    Then OrangeHRM should show login error "Invalid credentials"

