from orangehrm.models.pim import EmployeeSearchCriteria
from orangehrm.pages.employee_list_page import EmployeeListPage
from orangehrm.services.pim_service import PimService


class PimWorkflow:
    """Business workflows for employee search."""

    def __init__(self, pim_service: PimService) -> None:
        self.pim_service = pim_service

    def search_for_employees(self, criteria: EmployeeSearchCriteria) -> EmployeeListPage:
        return self.pim_service.search_employees(criteria)

    def should_show_employee_results(self, employee_list_page: EmployeeListPage) -> None:
        self.pim_service.assert_results_available(employee_list_page)

    def should_keep_search_criteria(self, employee_list_page: EmployeeListPage, criteria: EmployeeSearchCriteria) -> None:
        self.pim_service.assert_search_criteria_kept(employee_list_page, criteria)

