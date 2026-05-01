@sauce @checkout @e2e @regression
Feature: SauceDemo checkout e2e
  As a SauceDemo shopper
  I want to complete checkout from inventory to confirmation
  So that I can understand a full end-to-end BDD flow

  Background:
    Given a standard SauceDemo user is logged in
  @test
  Scenario: Complete checkout for two products
    When the user adds these products to the cart:
      | product_name          |
      | Sauce Labs Backpack   |
      | Sauce Labs Bike Light |
    And the user opens the cart
    And the user starts checkout
    And the user enters checkout information:
      | first_name | last_name | postal_code |
      | Alex       | Tester    | 12345       |
    Then the checkout overview should contain these products:
      | product_name          | price  |
      | Sauce Labs Backpack   | $29.99 |
      | Sauce Labs Bike Light | $9.99  |
    And the checkout item total should be "$39.98"
    When the user finishes checkout
    Then the checkout complete page should show "Thank you for your order!"

  Scenario: Checkout requires customer information
    When the user adds "Sauce Labs Backpack" to the cart
    And the user opens the cart
    And the user starts checkout
    And the user continues checkout without customer information
    Then checkout information error should be "Error: First Name is required"
