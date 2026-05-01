"""Step definitions for SauceDemo inventory regression scenarios."""

from pytest_bdd import parsers, scenarios, then, when

from pages.sd_inventory_page import SauceInventoryPage
from tests.steps.saucedemo.helpers import data_table_to_dicts


scenarios("saucedemo/saucedemo_inventory_regression.feature")


@then("the inventory page should show these products:")
def verify_inventory_products(inventory_page: SauceInventoryPage, datatable: list[list[str]]) -> None:
    inventory_page.assert_product_values(data_table_to_dicts(datatable))


@when(parsers.parse('the user sorts inventory by "{sort_option}"'))
def sort_inventory(inventory_page: SauceInventoryPage, sort_option: str) -> None:
    inventory_page.sort_by(sort_option)


@then("product prices should be sorted from low to high")
def verify_inventory_prices_are_sorted(inventory_page: SauceInventoryPage) -> None:
    inventory_page.assert_prices_sorted_low_to_high()
