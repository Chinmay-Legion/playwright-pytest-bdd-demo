@orangehrm @pim @regression
Feature: PIM employee search
  As an HR administrator
  I want to search employee records from PIM
  So that I can find employees without coupling BDD steps to page locators

  Background:
    Given an OrangeHRM administrator is signed in

  Scenario: Search employee records with reusable criteria
    When the user searches the PIM employee list with criteria:
      | employee_name | employee_id | employment_status | include                |
      |               | 0001        |                   | Current Employees Only |
    Then PIM employee results should be displayed
    And the PIM search form should keep the selected criteria

  Scenario: Search employee records by employment status
    When the user searches the PIM employee list with criteria:
      | employee_name | employee_id | employment_status | include                |
      |               |             | Full-Time Contract | Current Employees Only |
    Then PIM employee results should be displayed
    And the PIM search form should keep the selected criteria

