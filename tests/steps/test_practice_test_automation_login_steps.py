from pytest_bdd import given, parsers, scenarios, then
from playwright.sync_api import Page

from pages.pta_login_page import PtaLoginPage
from pages.pta_successful_page import PtaSuccessfulPage


scenarios("practice_test_automation_login.feature")


@given("the user is on the PTA login page", target_fixture="login_page")
def navigate_to_pta_login(page: Page) -> PtaLoginPage:
    login_page = PtaLoginPage(page)
    login_page.navigate()
    return login_page


@then("the user should land on the login successful page")
def verify_successful_login(page: Page) -> None:
#     page.screencast.show_chapter("Successful Login Page",
#     description="Logout button should be visible",
#     duration=500,
# )
#     page.screencast.show_actions(position="top-right")
    successfulpage = PtaSuccessfulPage(page)
    successfulpage.assert_login_successful()
    successfulpage.click_logout_button()


@then(parsers.re(r'the error message should read "(?P<expected_error>[^"]+)"'))
def verify_error_message(login_page: PtaLoginPage, expected_error: str) -> None:
    login_page.assert_error_text(expected_error)
