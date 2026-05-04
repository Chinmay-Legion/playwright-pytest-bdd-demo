from orangehrm.models.leave import LeaveFilter
from orangehrm.pages.leave_list_page import LeaveListPage
from orangehrm.services.leave_service import LeaveService


class LeaveWorkflow:
    """Business workflows for Leave navigation and filtering."""

    def __init__(self, leave_service: LeaveService) -> None:
        self.leave_service = leave_service

    def filter_leave_records(self, leave_filter: LeaveFilter) -> LeaveListPage:
        return self.leave_service.filter_leave_records(leave_filter)

    def should_show_leave_results(self, leave_list_page: LeaveListPage) -> None:
        self.leave_service.assert_results_available(leave_list_page)

    def should_keep_filter_values(self, leave_list_page: LeaveListPage, leave_filter: LeaveFilter) -> None:
        self.leave_service.assert_filter_kept(leave_list_page, leave_filter)

