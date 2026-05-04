from orangehrm.models.auth import OrangeHrmUser
from orangehrm.pages.dashboard_page import DashboardPage
from orangehrm.services.authentication_service import AuthenticationService


class AuthenticationWorkflow:
    """Business workflows for OrangeHRM authentication."""

    def __init__(self, authentication_service: AuthenticationService) -> None:
        self.authentication_service = authentication_service

    def sign_in_as(self, user: OrangeHrmUser) -> DashboardPage:
        return self.authentication_service.login_as(user)

    def attempt_sign_in(self, user: OrangeHrmUser) -> None:
        self.authentication_service.attempt_login(user)

    def should_reject_login(self, expected_message: str) -> None:
        self.authentication_service.assert_login_error(expected_message)

