from pytest_bdd import given, scenarios, then
from playwright.sync_api import Page

from pages.sd_login_page import SauceLoginPage
from pages.sd_product_page import SauceProductPage


scenarios("saucedemo_login.feature")


@given("the user is on the SauceDemo login page", target_fixture="login_page")
def navigate_to_sd_login(page: Page) -> SauceLoginPage:
    login_page = SauceLoginPage(page)
    login_page.navigate()
    return login_page


@then("the user should land on the products page")
def verify_products_page(page: Page) -> None:
    SauceProductPage(page).assert_on_products_page()


@then("the login error message should be displayed")
def verify_login_error(login_page: SauceLoginPage) -> None:
    login_page.assert_error_visible()
