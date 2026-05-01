"""SauceDemo-only fixtures and shared BDD steps.

This nested conftest.py applies only to tests under tests/steps/saucedemo.
It demonstrates fixture dependency injection and fixture chaining without adding
those SauceDemo details to the project-level tests/conftest.py file.
"""

import pytest
from pytest_bdd import given, parsers, then, when
from playwright.sync_api import Page

from pages.sd_cart_page import SauceCartPage
from pages.sd_checkout_step_one_page import SauceCheckoutStepOnePage
from pages.sd_inventory_page import SauceInventoryPage
from pages.sd_login_page import SauceLoginPage
from tests.steps.saucedemo.helpers import product_names_from_datatable


@pytest.fixture
def sauce_user() -> dict[str, str]:
    """Provide SauceDemo credentials as injectable test data."""

    return {"username": "standard_user", "password": "secret_sauce"}


@pytest.fixture
def sauce_login_page(page: Page) -> SauceLoginPage:
    """Create and navigate the login page using pytest-playwright's page fixture."""

    login_page = SauceLoginPage(page)
    login_page.navigate()
    return login_page


@pytest.fixture
def authenticated_inventory_page(sauce_login_page: SauceLoginPage, sauce_user: dict[str, str], page: Page) -> SauceInventoryPage:
    """Fixture chaining example: login page plus user data creates inventory state."""

    sauce_login_page.login(sauce_user["username"], sauce_user["password"])
    inventory_page = SauceInventoryPage(page)
    inventory_page.assert_loaded()
    return inventory_page


@given("a standard SauceDemo user is logged in", target_fixture="inventory_page")
def standard_sauce_user_is_logged_in(authenticated_inventory_page: SauceInventoryPage) -> SauceInventoryPage:
    """Expose the authenticated inventory page as a BDD fixture."""

    return authenticated_inventory_page


@when(parsers.parse('the user adds "{product_name}" to the cart'))
def add_product_to_cart(inventory_page: SauceInventoryPage, product_name: str) -> None:
    inventory_page.add_product_to_cart(product_name)


@when("the user adds these products to the cart:")
def add_products_to_cart(inventory_page: SauceInventoryPage, datatable: list[list[str]]) -> None:
    for product_name in product_names_from_datatable(datatable):
        inventory_page.add_product_to_cart(product_name)


@when(parsers.parse('the user removes "{product_name}" from the inventory'))
def remove_product_from_inventory(inventory_page: SauceInventoryPage, product_name: str) -> None:
    inventory_page.remove_product_from_inventory(product_name)


@when("the user opens the cart", target_fixture="cart_page")
def open_cart(inventory_page: SauceInventoryPage, page: Page) -> SauceCartPage:
    inventory_page.open_cart()
    cart_page = SauceCartPage(page)
    cart_page.assert_loaded()
    return cart_page


@when("the user continues shopping", target_fixture="inventory_page")
def continue_shopping(cart_page: SauceCartPage, page: Page) -> SauceInventoryPage:
    cart_page.continue_shopping()
    inventory_page = SauceInventoryPage(page)
    inventory_page.assert_loaded()
    return inventory_page


@when("the user starts checkout", target_fixture="checkout_step_one_page")
def start_checkout(cart_page: SauceCartPage, page: Page) -> SauceCheckoutStepOnePage:
    cart_page.start_checkout()
    checkout_page = SauceCheckoutStepOnePage(page)
    checkout_page.assert_loaded()
    return checkout_page


@then("the inventory page should be displayed")
def verify_inventory_page_is_displayed(inventory_page: SauceInventoryPage) -> None:
    inventory_page.assert_loaded()


@then(parsers.parse("the cart badge should show {expected_count:d}"))
def verify_cart_badge_count(inventory_page: SauceInventoryPage, expected_count: int) -> None:
    inventory_page.assert_cart_badge_count(expected_count)


@then("the cart badge should be empty")
def verify_cart_badge_is_empty(inventory_page: SauceInventoryPage) -> None:
    inventory_page.assert_cart_badge_empty()
