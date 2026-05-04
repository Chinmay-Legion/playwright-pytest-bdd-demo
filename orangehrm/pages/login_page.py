from playwright.sync_api import Page, expect

from orangehrm.models.auth import OrangeHrmUser
from orangehrm.pages.base import OrangeHrmBasePage


class LoginPage(OrangeHrmBasePage):
    """OrangeHRM authentication page object."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.error_message = page.locator(".oxd-alert-content-text")

    def navigate(self) -> None:
        self.goto_path("/web/index.php/auth/login")

    def login(self, user: OrangeHrmUser) -> None:
        self.username.fill(user.username)
        self.password.fill(user.password)
        self.login_button.click()

    def assert_error_message(self, expected_message: str) -> None:
        expect(self.error_message).to_have_text(expected_message)

