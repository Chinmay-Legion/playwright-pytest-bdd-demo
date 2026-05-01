from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceInventoryPage(BasePage):
    """Inventory page object for product-list regression checks."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.locator("[data-test='title']")
        self.cart_link = page.locator("[data-test='shopping-cart-link']")
        self.cart_badge = page.locator("[data-test='shopping-cart-badge']")
        self.sort_dropdown = page.locator("[data-test='product-sort-container']")
        self.inventory_items = page.locator("[data-test='inventory-item']")

    def assert_loaded(self) -> None:
        """Assert that the inventory page is ready for product interactions."""

        expect(self.title).to_have_text("Products")
        expect(self.inventory_items.first).to_be_visible()

    def product_row(self, product_name: str):
        """Return the inventory row for a product name."""

        return self.inventory_items.filter(has_text=product_name).first

    def add_product_to_cart(self, product_name: str) -> None:
        """Add one product by using the button inside that product row."""

        self.product_row(product_name).get_by_role("button", name="Add to cart").click()

    def remove_product_from_inventory(self, product_name: str) -> None:
        """Remove one product from the cart while still on the inventory page."""

        self.product_row(product_name).get_by_role("button", name="Remove").click()

    def open_cart(self) -> None:
        """Open the shopping cart from the inventory page."""

        self.cart_link.click()

    def sort_by(self, option_label: str) -> None:
        """Sort inventory products using the visible dropdown option label."""

        self.sort_dropdown.select_option(label=option_label)

    def product_price(self, product_name: str) -> str:
        """Return the visible price text for one inventory product."""

        return self.product_row(product_name).locator("[data-test='inventory-item-price']").inner_text().strip()

    def visible_product_prices(self) -> list[float]:
        """Return all visible product prices as numbers in their current screen order."""

        prices = self.inventory_items.locator("[data-test='inventory-item-price']")
        return [float(prices.nth(index).inner_text().strip().replace("$", "")) for index in range(prices.count())]

    def assert_cart_badge_count(self, expected_count: int) -> None:
        """Assert the cart badge count after adding products."""

        expect(self.cart_badge).to_have_text(str(expected_count))

    def assert_cart_badge_empty(self) -> None:
        """Assert the cart badge is hidden after all products are removed."""

        expect(self.cart_badge).to_have_count(0)

    def assert_product_values(self, expected_products: list[dict[str, str]]) -> None:
        """Assert product names and prices using rows from a BDD data table."""

        for expected_product in expected_products:
            product_name = expected_product["product_name"]
            expect(self.product_row(product_name)).to_be_visible()
            assert self.product_price(product_name) == expected_product["price"]

    def assert_prices_sorted_low_to_high(self) -> None:
        """Assert the current inventory prices are sorted ascending."""

        prices = self.visible_product_prices()
        assert prices == sorted(prices)
