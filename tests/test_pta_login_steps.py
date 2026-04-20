from pytest_bdd import given, then, scenarios, parsers
from playwright.sync_api import Page

from pages.pta_login_page import PtaLoginPage
from pages.pta_successful_page import PtaSuccessfulPage

scenarios("pta_login.feature")


@given("the user is on the PTA login page", target_fixture="login_page")
def navigate_to_pta_login(page: Page) -> PtaLoginPage:
    login_page = PtaLoginPage(page)
    login_page.navigate()
    return login_page


@then("the user should land on the login successful page")
def verify_successful_login(page: Page) -> None:
    PtaSuccessfulPage(page).assert_login_successful()


# ── parsers.re with a named capture group ────────────────────────────────────
# WHY parsers.re over parsers.parse:
#   parsers.parse  →  uses Python's str.format() syntax: "{expected_error}"
#                     simple but can't express character classes or constraints
#
#   parsers.re     →  full regex; named groups (?P<name>...) become parameters
#                     [^"]+ means "one or more characters that aren't a quote"
#                     This prevents greedy matching from swallowing the closing "
#
# This single step replaces the old verify_wrong_username_error AND
# verify_wrong_password_error steps — the expected text is data, not code.
#
@then(parsers.re(r'the error message should read "(?P<expected_error>[^"]+)"'))
def verify_error_message(login_page: PtaLoginPage, expected_error: str) -> None:
    login_page.assert_error_text(expected_error)
    login_page.assert_error_text

