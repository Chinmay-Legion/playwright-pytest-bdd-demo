from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceCheckoutStepTwoPage(BasePage):
    """Checkout overview page object for final order review."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.locator("[data-test='title']")
        self.checkout_items = page.locator("[data-test='inventory-item']")
        self.item_total = page.locator("[data-test='subtotal-label']")
        self.finish_button = page.locator("[data-test='finish']")

    def assert_loaded(self) -> None:
        """Assert that the checkout overview page is visible."""

        expect(self.title).to_have_text("Checkout: Overview")

    def overview_row(self, product_name: str):
        """Return the checkout overview row for a product name."""

        return self.checkout_items.filter(has_text=product_name).first

    def product_price(self, product_name: str) -> str:
        """Return the overview price for one product."""

        return self.overview_row(product_name).locator("[data-test='inventory-item-price']").inner_text().strip()

    def finish_checkout(self) -> None:
        """Finish the checkout flow."""

        self.finish_button.click()

    def assert_product_values(self, expected_products: list[dict[str, str]]) -> None:
        """Assert checkout overview products using a BDD data table."""

        for expected_product in expected_products:
            product_name = expected_product["product_name"]
            expect(self.overview_row(product_name)).to_be_visible()
            assert self.product_price(product_name) == expected_product["price"]

    def assert_item_total(self, expected_total: str) -> None:
        """Assert the item subtotal text before tax."""

        expect(self.item_total).to_have_text(f"Item total: {expected_total}")
