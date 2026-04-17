from pytest_bdd import given, then, scenarios
from playwright.sync_api import Page

from pages.sd_login_page import SauceLoginPage
from pages.sd_product_page import SauceProductPage

# Links every scenario in this feature to the step definitions below (and conftest.py)
# bdd_features_base_dir in pyproject.toml means the path is relative to tests/
scenarios("sd_login.feature")


# ── target_fixture="login_page" ──────────────────────────────────────────────
# This @given step does two things:
#   1. Navigates to the page (the "Given" action)
#   2. Returns the page object, which pytest-bdd registers as a fixture named
#      "login_page" — available to all subsequent steps in this scenario.
#
# The shared @when step in conftest.py receives it as `login_page`.
# No re-instantiation. No global state. Pure fixture injection.
#
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
