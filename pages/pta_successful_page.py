from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class PtaSuccessfulPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.logout_button = page.get_by_text("Log out")
        self.success_heading = page.get_by_role("heading", name="Logged In Successfully")

    def assert_login_successful(self) -> None:
        expect(self.success_heading).to_be_visible()
        expect(self.logout_button).to_be_visible()

    def click_logout_button(self) -> None:
        # expect(self.logout_button).to_be_visible()
        self.logout_button.click()
