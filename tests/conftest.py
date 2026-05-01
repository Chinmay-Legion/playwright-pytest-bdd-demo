from pathlib import Path

import allure
import pytest
from pytest_bdd import parsers, when


def pytest_html_report_title(report):
    report.title = "BDD Automation Report"


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    browser_args = list(browser_type_launch_args.get("args", []))

    if "--start-maximized" not in browser_args:
        browser_args.append("--start-maximized")

    return {**browser_type_launch_args, "args": browser_args}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "no_viewport": True}


@pytest.fixture(autouse=True)
def attach_playwright_traces_to_allure(output_path: str):
    yield

    for trace_path in sorted(Path(output_path).glob("trace*.zip")):
        allure.attach.file(
            str(trace_path),
            name=trace_path.name,
            attachment_type="application/zip",
            extension="zip",
        )


# Shared by both login features. Each feature's Given step returns a site-specific
# page object as the "login_page" fixture, so this action stays reusable.
@when(parsers.re(r'the user logs in with username "(?P<username>[^"]*)" and password "(?P<password>[^"]*)"'))
def login_with_credentials(login_page, username: str, password: str) -> None:
#     page.screencast.show_chapter("Login With Credentials",
#     description=f"Username - {username} , Password - {password}",
#     duration=500,
# )
#     page.screencast.show_overlay('<div style="color: red">Whats up</div>')
#     page.screencast.show_actions(position="top-right")
    login_page.login(username, password)
