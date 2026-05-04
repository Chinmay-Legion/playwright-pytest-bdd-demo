"""OrangeHRM fixtures and shared BDD steps.

This file demonstrates dependency injection and fixture chaining:

page -> page objects -> services -> workflows -> BDD steps

Feature files stay business-readable. Step definitions translate Gherkin to
workflow calls. The workflow/service/page layers absorb complexity as the suite
grows.
"""

import os

import pytest
from playwright.sync_api import Page
from pytest_bdd import given

from orangehrm.components.side_navigation import SideNavigation
from orangehrm.models.auth import OrangeHrmUser
from orangehrm.pages.dashboard_page import DashboardPage
from orangehrm.pages.employee_list_page import EmployeeListPage
from orangehrm.pages.leave_list_page import LeaveListPage
from orangehrm.pages.login_page import LoginPage
from orangehrm.services.authentication_service import AuthenticationService
from orangehrm.services.leave_service import LeaveService
from orangehrm.services.navigation_service import NavigationService
from orangehrm.services.pim_service import PimService
from orangehrm.workflows.authentication_workflow import AuthenticationWorkflow
from orangehrm.workflows.leave_workflow import LeaveWorkflow
from orangehrm.workflows.pim_workflow import PimWorkflow


@pytest.fixture
def orangehrm_base_url() -> str:
    """Allow CI to override the demo host without changing test code."""

    return os.getenv("ORANGEHRM_BASE_URL", "https://opensource-demo.orangehrmlive.com")


@pytest.fixture
def orangehrm_admin_user() -> OrangeHrmUser:
    """Inject the public OrangeHRM demo administrator."""

    return OrangeHrmUser.demo_admin()


@pytest.fixture
def orangehrm_login_page(page: Page, orangehrm_base_url: str) -> LoginPage:
    """Create the login page object from pytest-playwright's page fixture."""

    return LoginPage(page, orangehrm_base_url)


@pytest.fixture
def orangehrm_dashboard_page(page: Page, orangehrm_base_url: str) -> DashboardPage:
    """Create the dashboard page object."""

    return DashboardPage(page, orangehrm_base_url)


@pytest.fixture
def orangehrm_employee_list_page(page: Page, orangehrm_base_url: str) -> EmployeeListPage:
    """Create the PIM employee list page object."""

    return EmployeeListPage(page, orangehrm_base_url)


@pytest.fixture
def orangehrm_leave_list_page(page: Page, orangehrm_base_url: str) -> LeaveListPage:
    """Create the Leave list page object."""

    return LeaveListPage(page, orangehrm_base_url)


@pytest.fixture
def orangehrm_side_navigation(page: Page) -> SideNavigation:
    """Create the shared side navigation component."""

    return SideNavigation(page)


@pytest.fixture
def orangehrm_authentication_service(
    orangehrm_login_page: LoginPage,
    orangehrm_dashboard_page: DashboardPage,
) -> AuthenticationService:
    """Fixture chaining: page objects become a domain service."""

    return AuthenticationService(orangehrm_login_page, orangehrm_dashboard_page)


@pytest.fixture
def orangehrm_navigation_service(
    orangehrm_side_navigation: SideNavigation,
    orangehrm_employee_list_page: EmployeeListPage,
    orangehrm_leave_list_page: LeaveListPage,
) -> NavigationService:
    """Fixture chaining: shared navigation composes with destination pages."""

    return NavigationService(orangehrm_side_navigation, orangehrm_employee_list_page, orangehrm_leave_list_page)


@pytest.fixture
def orangehrm_pim_service(orangehrm_navigation_service: NavigationService) -> PimService:
    """Create the PIM service from the navigation service."""

    return PimService(orangehrm_navigation_service)


@pytest.fixture
def orangehrm_leave_service(orangehrm_navigation_service: NavigationService) -> LeaveService:
    """Create the Leave service from the navigation service."""

    return LeaveService(orangehrm_navigation_service)


@pytest.fixture
def orangehrm_authentication_workflow(orangehrm_authentication_service: AuthenticationService) -> AuthenticationWorkflow:
    """Fixture chaining: service becomes a business workflow."""

    return AuthenticationWorkflow(orangehrm_authentication_service)


@pytest.fixture
def orangehrm_pim_workflow(orangehrm_pim_service: PimService) -> PimWorkflow:
    """Create the PIM business workflow."""

    return PimWorkflow(orangehrm_pim_service)


@pytest.fixture
def orangehrm_leave_workflow(orangehrm_leave_service: LeaveService) -> LeaveWorkflow:
    """Create the Leave business workflow."""

    return LeaveWorkflow(orangehrm_leave_service)


@given("an OrangeHRM administrator is signed in", target_fixture="signed_in_dashboard_page")
def orangehrm_administrator_is_signed_in(
    orangehrm_authentication_workflow: AuthenticationWorkflow,
    orangehrm_admin_user: OrangeHrmUser,
) -> DashboardPage:
    """Shared authenticated precondition for OrangeHRM business features."""

    return orangehrm_authentication_workflow.sign_in_as(orangehrm_admin_user)

