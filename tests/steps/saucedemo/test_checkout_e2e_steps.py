"""Step definitions for SauceDemo checkout end-to-end scenarios."""

from pytest_bdd import parsers, scenarios, then, when
from playwright.sync_api import Page

from pages.sd_checkout_complete_page import SauceCheckoutCompletePage
from pages.sd_checkout_step_one_page import SauceCheckoutStepOnePage
from pages.sd_checkout_step_two_page import SauceCheckoutStepTwoPage
from tests.steps.saucedemo.helpers import data_table_to_dicts


scenarios("saucedemo/saucedemo_checkout_e2e.feature")


@when("the user enters checkout information:", target_fixture="checkout_step_two_page")
def enter_checkout_information(checkout_step_one_page: SauceCheckoutStepOnePage, page: Page, datatable: list[list[str]]) -> SauceCheckoutStepTwoPage:
    customer = data_table_to_dicts(datatable)[0]
    checkout_step_one_page.enter_customer_information(customer["first_name"], customer["last_name"], customer["postal_code"])

    checkout_step_two_page = SauceCheckoutStepTwoPage(page)
    checkout_step_two_page.assert_loaded()
    return checkout_step_two_page


@when("the user continues checkout without customer information")
def continue_checkout_without_customer_information(checkout_step_one_page: SauceCheckoutStepOnePage) -> None:
    checkout_step_one_page.continue_without_information()


@then("the checkout overview should contain these products:")
def verify_checkout_overview_products(checkout_step_two_page: SauceCheckoutStepTwoPage, datatable: list[list[str]]) -> None:
    checkout_step_two_page.assert_product_values(data_table_to_dicts(datatable))


@then(parsers.parse('the checkout item total should be "{expected_total}"'))
def verify_checkout_item_total(checkout_step_two_page: SauceCheckoutStepTwoPage, expected_total: str) -> None:
    checkout_step_two_page.assert_item_total(expected_total)


@when("the user finishes checkout", target_fixture="checkout_complete_page")
def finish_checkout(checkout_step_two_page: SauceCheckoutStepTwoPage, page: Page) -> SauceCheckoutCompletePage:
    checkout_step_two_page.finish_checkout()
    checkout_complete_page = SauceCheckoutCompletePage(page)
    checkout_complete_page.assert_loaded()
    return checkout_complete_page


@then(parsers.parse('the checkout complete page should show "{expected_message}"'))
def verify_checkout_complete_message(checkout_complete_page: SauceCheckoutCompletePage, expected_message: str) -> None:
    checkout_complete_page.assert_complete_message(expected_message)


@then(parsers.parse('checkout information error should be "{expected_error}"'))
def verify_checkout_information_error(checkout_step_one_page: SauceCheckoutStepOnePage, expected_error: str) -> None:
    checkout_step_one_page.assert_error_text(expected_error)
