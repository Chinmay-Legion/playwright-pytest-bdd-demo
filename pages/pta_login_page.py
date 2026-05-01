from playwright.sync_api import Page, expect

from pages.base_page import BasePage

_URL = "https://practicetestautomation.com/practice-test-login/"


class PtaLoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.submit_btn = page.locator("#submit")
        self.error_message = page.locator("#error")

    def navigate(self) -> None:
        super().navigate(_URL)

    # Single action: fill credentials AND submit — the full "login" user action
    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_btn.click()

    def assert_error_text(self, expected_text: str) -> None:
        expect(self.error_message).to_be_visible()
        expect(self.error_message).to_have_text(expected_text)
