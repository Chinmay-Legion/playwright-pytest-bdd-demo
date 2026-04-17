import pytest
from pytest_bdd import when,then, parsers
from playwright.sync_api import BrowserContext


# ── HTML report title ────────────────────────────────────────────────────────
def pytest_html_report_title(report):
    report.title = "BDD Automation Report"


# ── Browser context: 1920×1080 viewport for all tests ───────────────────────
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "viewport": {"width": 1920, "height": 1080}}


# ── Shared @when step ────────────────────────────────────────────────────────
#
# WHY it lives here instead of each step file:
#   Both features use identical step text. Defining it once in conftest.py
#   makes it available to every scenario without duplication or shadowing.
#
# HOW it works with target_fixture:
#   The @given step in each step file uses target_fixture="login_page" to
#   return the correct page object (SauceLoginPage or PtaLoginPage).
#   pytest-bdd injects that object here as `login_page`.
#
# REGEX breakdown:
#   (?P<username>[^"]*) — named group; [^"]* matches any chars except a quote
#                         (zero-or-more so empty strings are valid too)
#   (?P<password>[^"]*) — same for password
#   Named groups become function parameters automatically.
#
@when(parsers.re(r'the user logs in with username "(?P<username>[^"]*)" and password "(?P<password>[^"]*)"'))
def login_with_credentials(login_page, username: str, password: str) -> None:
    login_page.login(username, password)

@then(parsers.parse('there are {items} items in the {section} section'))
def step_impl(items,section):
    print(items)
    print(section)