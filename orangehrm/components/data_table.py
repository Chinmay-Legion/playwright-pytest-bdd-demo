import re

from playwright.sync_api import Page, expect


class DataTableComponent:
    """Reusable OrangeHRM table assertions."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.cards = page.locator(".oxd-table-card")
        self.records_label = page.get_by_text(re.compile(r"(No )?Records? Found", re.IGNORECASE)).first

    def assert_result_summary_visible(self) -> None:
        expect(self.records_label).to_be_visible()

    def assert_table_is_present(self) -> None:
        expect(self.page.locator(".oxd-table").first).to_be_visible()

    def assert_search_feedback_visible(self) -> None:
        """Accept either matching rows or the valid empty-state banner."""

        self.assert_result_summary_visible()
