@learning @datatable
Feature: Pytest-bdd data table examples
  These scenarios do not open a browser.
  They show different ways to read BDD data tables in step definitions.

  Scenario: Read a single-column data table as a list
    Given these product names:
      | product_name        |
      | Sauce Labs Backpack |
      | Sauce Labs Bike Light |
      | Sauce Labs Onesie   |
    Then the product list should contain 3 products
    And the product list should include "Sauce Labs Onesie"

  Scenario: Read a two-column data table as settings
    Given these checkout settings:
      | field      | value  |
      | first_name | Alex   |
      | last_name  | Tester |
      | postal_code | 12345 |
    Then the checkout setting "first_name" should be "Alex"
    And the checkout setting "postal_code" should be "12345"

  Scenario: Read a multi-column data table as rows
    Given these course records:
      | course_name          | language | level        | enrollments |
      | Selenium with Python | Python   | Beginner     | 10705       |
      | REST Assured         | Java     | Intermediate | 8254        |
      | Selenium with Java   | Java     | Beginner     | 64284       |
    Then there should be 2 courses with language "Java"
    And the most popular course should be "Selenium with Java"

  Scenario: Use data tables on both Given and Then steps
    Given these visible table rows:
      | course_name          | language | level    |
      | Python for Testers   | Python   | Beginner |
      | Selenium with Python | Python   | Beginner |
    Then the rows should match exactly:
      | course_name          | language | level    |
      | Python for Testers   | Python   | Beginner |
      | Selenium with Python | Python   | Beginner |
