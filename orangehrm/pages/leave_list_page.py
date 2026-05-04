from playwright.sync_api import Page, expect

from orangehrm.components.data_table import DataTableComponent
from orangehrm.components.form import FormComponent
from orangehrm.components.top_bar import TopBar
from orangehrm.models.leave import LeaveFilter
from orangehrm.pages.base import OrangeHrmBasePage


class LeaveListPage(OrangeHrmBasePage):
    """Leave list page object for navigation and filter validation examples."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.form = FormComponent(page)
        self.table = DataTableComponent(page)
        self.top_bar = TopBar(page)
        self.search_button = page.get_by_role("button", name="Search")
        self.leave_list_heading = page.get_by_role("heading", name="Leave List")

    def assert_loaded(self) -> None:
        self.top_bar.assert_module("Leave")
        expect(self.leave_list_heading).to_be_visible()

    def apply_filter(self, leave_filter: LeaveFilter) -> None:
        self.form.fill_text("From Date", leave_filter.from_date)
        self.form.fill_text("To Date", leave_filter.to_date)
        self.form.select_option("Show Leave with Status", leave_filter.status)
        self.form.select_option("Leave Type", leave_filter.leave_type)
        self.form.choose_autocomplete("Employee Name", leave_filter.employee_name)
        self.form.select_option("Sub Unit", leave_filter.sub_unit)
        self.search_button.click()

    def assert_results_available(self) -> None:
        self.table.assert_search_feedback_visible()

    def assert_filter_kept(self, leave_filter: LeaveFilter) -> None:
        self.form.assert_text_value("From Date", leave_filter.from_date)
        self.form.assert_group_contains("Show Leave with Status", leave_filter.status)
        self.form.assert_group_contains("Leave Type", leave_filter.leave_type)
        self.form.assert_group_contains("Employee Name", leave_filter.employee_name)
        self.form.assert_group_contains("Sub Unit", leave_filter.sub_unit)
