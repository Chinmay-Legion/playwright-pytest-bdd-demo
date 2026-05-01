from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceProductPage(BasePage):
    """Small compatibility page object used by the original login scenarios."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.product_label = page.locator("[data-test='title']")

    def assert_on_products_page(self) -> None:
        expect(self.product_label).to_have_text("Products")
