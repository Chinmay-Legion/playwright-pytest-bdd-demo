from playwright.sync_api import Page, expect  # was incorrectly async_api

from pages.base_page import BasePage


class SauceProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.product_label = page.locator(".title")

    def assert_on_products_page(self) -> None:
        expect(self.product_label).to_have_text("Products")
