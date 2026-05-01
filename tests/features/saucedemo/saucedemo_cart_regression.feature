@sauce @cart @regression
Feature: SauceDemo cart regression
  As a SauceDemo shopper
  I want the cart to keep my selected products
  So that I can review them before checkout

  Background:
    Given a standard SauceDemo user is logged in

  Scenario: Cart lists products added from inventory
    When the user adds these products to the cart:
      | product_name          |
      | Sauce Labs Backpack   |
      | Sauce Labs Bike Light |
    And the user opens the cart
    Then the cart page should be displayed
    And the cart item count should be 2
    And the cart should contain these products:
      | product_name          | price  |
      | Sauce Labs Backpack   | $29.99 |
      | Sauce Labs Bike Light | $9.99  |

  Scenario: Continue shopping from the cart returns to inventory
    When the user adds "Sauce Labs Onesie" to the cart
    And the user opens the cart
    And the user continues shopping
    Then the inventory page should be displayed
    And the cart badge should show 1
