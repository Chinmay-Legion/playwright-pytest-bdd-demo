import pytest
from pytest_bdd import when,then, parsers,step
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
@when(parsers.re(r'the user logs in with username (?P<username>[^"]*) and password (?P<password>[^"]*)'))
def login_with_credentials(login_page, username: str, password: str) -> None:
    login_page.login(username, password)

@then(parsers.parse('there are {items} items in the {section} section'))
def step_impl(items,section):
    print(items)
    print(section)



from functools import partial

EXTRA_TYPES = {"Number": int, "Price": float}
parse_typed = partial(parsers.cfparse, extra_types=EXTRA_TYPES)

@then(parse_typed("the user pays {amount:Number}"))
def step_when_user_pays(amount): 
    print(f"AMOUNT IS {amount}")


EXTRA_TYPES = {"Number": int, "Price": float}

@step(
    parsers.cfparse("the order total is {amount:Number}", extra_types=EXTRA_TYPES),
    target_fixture="order_amount"
)
def step_given_order_total(amount):
    print(f"TOTAL IS {amount}")


# Using parsers.re
@step(parsers.re(r'I have (?P<count>five|six) products'))
def step_impl(count):
    print(f"I HAVE THIS MANY PRODUCTS {count}")


@step(parsers.re(r'the (?P<button>submit|cancel|reset) button is (?P<state>enabled|disabled)'))
def step_when_button_is_state(page, button, state):
    print("2")

@step(parsers.re(r'the (?P<user>admin|editor|poster) (?P<bool>is|is not) in the (?P<place>office|canteen|washroom)'))
def step_when_button_is_state(page, button, state):
    print("2")




@then(parsers.parse("the user presses on the {button}"))
def step_the_user_presses_on_the_button(button):
    raise NotImplementedError("step not implemented")
