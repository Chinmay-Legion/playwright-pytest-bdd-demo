from orangehrm.models.pim import EmployeeSearchCriteria
from orangehrm.pages.employee_list_page import EmployeeListPage
from orangehrm.services.navigation_service import NavigationService


class PimService:
    """Reusable PIM employee actions."""

    def __init__(self, navigation_service: NavigationService) -> None:
        self.navigation_service = navigation_service

    def search_employees(self, criteria: EmployeeSearchCriteria) -> EmployeeListPage:
        employee_list_page = self.navigation_service.open_pim_employee_list()
        employee_list_page.search(criteria)
        return employee_list_page

    def assert_results_available(self, employee_list_page: EmployeeListPage) -> None:
        employee_list_page.assert_results_available()

    def assert_search_criteria_kept(self, employee_list_page: EmployeeListPage, criteria: EmployeeSearchCriteria) -> None:
        employee_list_page.assert_criteria_kept(criteria)

