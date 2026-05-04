@orangehrm @leave @regression
Feature: Leave page navigation and filter validation
  As an HR administrator
  I want to navigate to Leave and validate filter behavior
  So that reusable workflows can support more leave-management scenarios later

  Background:
    Given an OrangeHRM administrator is signed in

  Scenario: Filter leave records by date range and status
    When the user filters leave records with:
      | from_date  | to_date    | status           | leave_type | employee_name | sub_unit |
      | 2026-01-01 | 2026-12-31 | Pending Approval |            |               |          |
    Then Leave results should be displayed
    And the Leave filter form should keep the selected criteria

  Scenario: Filter leave records by date range only
    When the user filters leave records with:
      | from_date  | to_date    | status | leave_type | employee_name | sub_unit |
      | 2026-01-01 | 2026-12-31 |        |            |               |          |
    Then Leave results should be displayed
    And the Leave filter form should keep the selected criteria

