from playwright.sync_api import Page, expect

from pages.base_page import BasePage

_URL = "https://www.saucedemo.com/v1/"


class SauceLoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input = page.locator("#user-name")
        self.password_input = page.locator("#password")
        self.login_btn = page.locator("#login-button")
        self.error_message = page.locator("[data-test='error']")

    def navigate(self) -> None:
        super().navigate(_URL)

    # Single action: fill credentials AND click — the full "login" user action
    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()

    def assert_error_visible(self) -> None:
        expect(self.error_message).to_be_visible()
