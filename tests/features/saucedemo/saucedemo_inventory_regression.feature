@sauce @inventory @regression
Feature: SauceDemo inventory regression
  As a SauceDemo shopper
  I want the inventory page to show products correctly
  So that I can trust the product catalog before checkout

  Background:
    Given a standard SauceDemo user is logged in

  @smoke @smoke_sd
  Scenario: Inventory catalog is visible with known products
    Then the inventory page should be displayed
    And the inventory page should show these products:
      | product_name              | price  |
      | Sauce Labs Backpack       | $29.99 |
      | Sauce Labs Bike Light     | $9.99  |
      | Sauce Labs Fleece Jacket  | $49.99 |

  Scenario: Sort inventory by price low to high
    When the user sorts inventory by "Price (low to high)"
    Then product prices should be sorted from low to high

  Scenario: Add and remove a product from the inventory page
    When the user adds "Sauce Labs Backpack" to the cart
    Then the cart badge should show 1
    When the user removes "Sauce Labs Backpack" from the inventory
    Then the cart badge should be empty
