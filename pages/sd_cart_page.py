from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceCartPage(BasePage):
    """Cart page object for cart regression and checkout handoff checks."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.locator("[data-test='title']")
        self.cart_items = page.locator("[data-test='inventory-item']")
        self.checkout_button = page.locator("[data-test='checkout']")
        self.continue_shopping_button = page.locator("[data-test='continue-shopping']")

    def assert_loaded(self) -> None:
        """Assert that the cart page is visible."""

        expect(self.title).to_have_text("Your Cart")

    def cart_row(self, product_name: str):
        """Return the cart row for a product name."""

        return self.cart_items.filter(has_text=product_name).first

    def product_price(self, product_name: str) -> str:
        """Return the visible cart price for one product."""

        return self.cart_row(product_name).locator("[data-test='inventory-item-price']").inner_text().strip()

    def start_checkout(self) -> None:
        """Click Checkout from the cart."""

        self.checkout_button.click()

    def continue_shopping(self) -> None:
        """Return to the inventory page from the cart."""

        self.continue_shopping_button.click()

    def assert_item_count(self, expected_count: int) -> None:
        """Assert the number of cart rows."""

        expect(self.cart_items).to_have_count(expected_count)

    def assert_product_values(self, expected_products: list[dict[str, str]]) -> None:
        """Assert cart product names and prices using a BDD data table."""

        for expected_product in expected_products:
            product_name = expected_product["product_name"]
            expect(self.cart_row(product_name)).to_be_visible()
            assert self.product_price(product_name) == expected_product["price"]
