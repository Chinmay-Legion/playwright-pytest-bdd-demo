"""Step definitions for SauceDemo cart regression scenarios."""

from pytest_bdd import parsers, scenarios, then

from pages.sd_cart_page import SauceCartPage
from tests.steps.saucedemo.helpers import data_table_to_dicts


scenarios("saucedemo/saucedemo_cart_regression.feature")


@then("the cart page should be displayed")
def verify_cart_page_is_displayed(cart_page: SauceCartPage) -> None:
    cart_page.assert_loaded()


@then(parsers.parse("the cart item count should be {expected_count:d}"))
def verify_cart_item_count(cart_page: SauceCartPage, expected_count: int) -> None:
    cart_page.assert_item_count(expected_count)


@then("the cart should contain these products:")
def verify_cart_products(cart_page: SauceCartPage, datatable: list[list[str]]) -> None:
    cart_page.assert_product_values(data_table_to_dicts(datatable))
