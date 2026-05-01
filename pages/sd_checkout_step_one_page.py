from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceCheckoutStepOnePage(BasePage):
    """Checkout information page object for customer details validation."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.locator("[data-test='title']")
        self.first_name_input = page.locator("[data-test='firstName']")
        self.last_name_input = page.locator("[data-test='lastName']")
        self.postal_code_input = page.locator("[data-test='postalCode']")
        self.continue_button = page.locator("[data-test='continue']")
        self.error_message = page.locator("[data-test='error']")

    def assert_loaded(self) -> None:
        """Assert that the checkout information page is visible."""

        expect(self.title).to_have_text("Checkout: Your Information")

    def enter_customer_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        """Fill the customer information form and continue to overview."""

        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)
        self.continue_button.click()

    def continue_without_information(self) -> None:
        """Submit the empty customer information form."""

        self.continue_button.click()

    def assert_error_text(self, expected_error: str) -> None:
        """Assert the checkout validation error text."""

        expect(self.error_message).to_have_text(expected_error)
