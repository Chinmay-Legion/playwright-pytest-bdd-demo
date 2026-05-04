from orangehrm.models.auth import OrangeHrmUser
from orangehrm.pages.dashboard_page import DashboardPage
from orangehrm.pages.login_page import LoginPage


class AuthenticationService:
    """Reusable authentication actions for OrangeHRM."""

    def __init__(self, login_page: LoginPage, dashboard_page: DashboardPage) -> None:
        self.login_page = login_page
        self.dashboard_page = dashboard_page

    def login_as(self, user: OrangeHrmUser) -> DashboardPage:
        self.login_page.navigate()
        self.login_page.login(user)
        self.dashboard_page.assert_loaded()
        return self.dashboard_page

    def attempt_login(self, user: OrangeHrmUser) -> None:
        self.login_page.navigate()
        self.login_page.login(user)

    def assert_login_error(self, expected_message: str) -> None:
        self.login_page.assert_error_message(expected_message)

    def logout(self) -> None:
        self.dashboard_page.logout()

