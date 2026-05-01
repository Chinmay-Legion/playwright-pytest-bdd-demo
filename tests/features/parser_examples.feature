@learning @parsers
Feature: Pytest-bdd parser examples
  These scenarios do not open a browser.
  They are small examples for learning how step parsers pass data into Python.

  Scenario: String steps match exact text
    Then the parser demo starts

  Scenario: Parse steps capture readable values
    Then there are 3 items in the cart section

  Scenario: Regex steps can restrict accepted words
    Then I have five products
    And the submit button is disabled

  Scenario: Cfparse steps convert values to Python types
    Given the order total is 42
    Then the user pays 12.50
    And the stored order total should be 42
