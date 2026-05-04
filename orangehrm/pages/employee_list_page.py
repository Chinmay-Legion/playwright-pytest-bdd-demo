from playwright.sync_api import Page, expect

from orangehrm.components.data_table import DataTableComponent
from orangehrm.components.form import FormComponent
from orangehrm.components.top_bar import TopBar
from orangehrm.models.pim import EmployeeSearchCriteria
from orangehrm.pages.base import OrangeHrmBasePage


class EmployeeListPage(OrangeHrmBasePage):
    """PIM employee list page object."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.form = FormComponent(page)
        self.table = DataTableComponent(page)
        self.top_bar = TopBar(page)
        self.search_button = page.get_by_role("button", name="Search")
        self.employee_information_heading = page.get_by_text("Employee Information")

    def assert_loaded(self) -> None:
        self.top_bar.assert_module("PIM")
        expect(self.employee_information_heading).to_be_visible()

    def search(self, criteria: EmployeeSearchCriteria) -> None:
        self.form.choose_autocomplete("Employee Name", criteria.employee_name)
        self.form.fill_text("Employee Id", criteria.employee_id)
        self.form.select_option("Employment Status", criteria.employment_status)
        self.form.select_option("Include", criteria.include)
        self.search_button.click()

    def assert_results_available(self) -> None:
        self.table.assert_table_is_present()
        self.table.assert_result_summary_visible()

    def assert_criteria_kept(self, criteria: EmployeeSearchCriteria) -> None:
        self.form.assert_group_contains("Employee Name", criteria.employee_name)
        self.form.assert_text_value("Employee Id", criteria.employee_id)
        self.form.assert_group_contains("Employment Status", criteria.employment_status)
        self.form.assert_group_contains("Include", criteria.include)

