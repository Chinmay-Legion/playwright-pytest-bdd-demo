from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceCheckoutCompletePage(BasePage):
    """Checkout completion page object for the final e2e assertion."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.locator("[data-test='title']")
        self.complete_header = page.locator("[data-test='complete-header']")

    def assert_loaded(self) -> None:
        """Assert that the checkout completion page is visible."""

        expect(self.title).to_have_text("Checkout: Complete!")

    def assert_complete_message(self, expected_message: str) -> None:
        """Assert the order completion message."""

        expect(self.complete_header).to_have_text(expected_message)
