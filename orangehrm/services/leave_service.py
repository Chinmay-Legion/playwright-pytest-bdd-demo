from orangehrm.models.leave import LeaveFilter
from orangehrm.pages.leave_list_page import LeaveListPage
from orangehrm.services.navigation_service import NavigationService


class LeaveService:
    """Reusable Leave module actions."""

    def __init__(self, navigation_service: NavigationService) -> None:
        self.navigation_service = navigation_service

    def filter_leave_records(self, leave_filter: LeaveFilter) -> LeaveListPage:
        leave_list_page = self.navigation_service.open_leave_list()
        leave_list_page.apply_filter(leave_filter)
        return leave_list_page

    def assert_results_available(self, leave_list_page: LeaveListPage) -> None:
        leave_list_page.assert_results_available()

    def assert_filter_kept(self, leave_list_page: LeaveListPage, leave_filter: LeaveFilter) -> None:
        leave_list_page.assert_filter_kept(leave_filter)

