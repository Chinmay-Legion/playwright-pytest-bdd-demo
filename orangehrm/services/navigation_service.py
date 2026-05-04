from orangehrm.components.side_navigation import SideNavigation
from orangehrm.pages.employee_list_page import EmployeeListPage
from orangehrm.pages.leave_list_page import LeaveListPage


class NavigationService:
    """Reusable module navigation actions."""

    def __init__(self, side_navigation: SideNavigation, employee_list_page: EmployeeListPage, leave_list_page: LeaveListPage) -> None:
        self.side_navigation = side_navigation
        self.employee_list_page = employee_list_page
        self.leave_list_page = leave_list_page

    def open_pim_employee_list(self) -> EmployeeListPage:
        self.side_navigation.open_module("PIM")
        self.employee_list_page.assert_loaded()
        return self.employee_list_page

    def open_leave_list(self) -> LeaveListPage:
        self.side_navigation.open_module("Leave")
        self.leave_list_page.assert_loaded()
        return self.leave_list_page

