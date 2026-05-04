from playwright.sync_api import Page, expect

from orangehrm.components.top_bar import TopBar
from orangehrm.pages.base import OrangeHrmBasePage


class DashboardPage(OrangeHrmBasePage):
    """Dashboard page reached after successful authentication."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.top_bar = TopBar(page)
        self.heading = page.get_by_role("heading", name="Dashboard")

    def assert_loaded(self) -> None:
        expect(self.heading).to_be_visible()
        self.top_bar.assert_user_menu_available()

    def logout(self) -> None:
        self.top_bar.logout()

