@pta @table
Feature: Practice Test Automation course table
  As a learner
  I want to practice table filters and row assertions
  So that I can understand Playwright table locators with pytest-bdd

  Background:
    Given the user is on the PTA table page

  @smoke
  Scenario: The course table is visible
    Then the course table should be displayed

  Scenario: Filter courses by language
    When the user filters the table by language "Java"
    Then every visible course should have language "Java"

  Scenario: Filter beginner Python courses with many enrollments
    When the user filters the table by language "Python"
    And the user keeps only level "Beginner"
    And the user sets minimum enrollments to "10,000+"
    Then every visible course should have language "Python"
    And every visible course should have level "Beginner"
    And every visible course should have at least 10000 enrollments

  Scenario: Sort courses by enrollments
    When the user sorts the table by "Enrollments"
    Then enrollments should be sorted from lowest to highest

  Scenario: Verify course details using a BDD data table
    Then the table should contain these courses:
      | course_name          | language | level        | enrollments |
      | Selenium with Python | Python   | Beginner     | 10705       |
      | REST Assured         | Java     | Intermediate | 8254        |
