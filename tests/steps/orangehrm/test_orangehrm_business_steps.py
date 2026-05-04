"""Thin pytest-bdd steps for all OrangeHRM business features.

This module intentionally loads multiple OrangeHRM feature files. The scalable
part is not "one step file per feature"; the scalable part is that each step
delegates to workflows, and workflows delegate to services and page objects.
"""

from pytest_bdd import given, parsers, scenarios, then, when

from orangehrm.models.auth import OrangeHrmUser
from orangehrm.models.leave import LeaveFilter
from orangehrm.models.pim import EmployeeSearchCriteria
from orangehrm.pages.dashboard_page import DashboardPage
from orangehrm.workflows.authentication_workflow import AuthenticationWorkflow
from orangehrm.workflows.leave_workflow import LeaveWorkflow
from orangehrm.workflows.pim_workflow import PimWorkflow
from tests.steps.orangehrm.helpers import EmployeeSearchContext, LeaveFilterContext, first_data_row


scenarios("orangehrm/authentication.feature")
scenarios("orangehrm/pim_employee_search.feature")
scenarios("orangehrm/leave_filter_validation.feature")


@given("an OrangeHRM administrator exists", target_fixture="orangehrm_user")
def orangehrm_administrator_exists() -> OrangeHrmUser:
    """Provide the demo admin user as business data."""

    return OrangeHrmUser.demo_admin()


@given("an OrangeHRM user has credentials:", target_fixture="orangehrm_user")
def orangehrm_user_has_credentials(datatable: list[list[str]]) -> OrangeHrmUser:
    """Create a user model from a BDD data table."""

    row = first_data_row(datatable)
    return OrangeHrmUser(username=row["username"], password=row["password"])


@when("the user logs in to OrangeHRM", target_fixture="signed_in_dashboard_page")
def user_logs_in_to_orangehrm(
    orangehrm_authentication_workflow: AuthenticationWorkflow,
    orangehrm_user: OrangeHrmUser,
) -> DashboardPage:
    return orangehrm_authentication_workflow.sign_in_as(orangehrm_user)


@when("the user attempts to login to OrangeHRM")
def user_attempts_to_login_to_orangehrm(
    orangehrm_authentication_workflow: AuthenticationWorkflow,
    orangehrm_user: OrangeHrmUser,
) -> None:
    orangehrm_authentication_workflow.attempt_sign_in(orangehrm_user)


@then("the OrangeHRM dashboard should be displayed")
def orangehrm_dashboard_should_be_displayed(signed_in_dashboard_page: DashboardPage) -> None:
    signed_in_dashboard_page.assert_loaded()


@then("the OrangeHRM user menu should be available")
def orangehrm_user_menu_should_be_available(signed_in_dashboard_page: DashboardPage) -> None:
    signed_in_dashboard_page.top_bar.assert_user_menu_available()


@then(parsers.parse('OrangeHRM should show login error "{expected_message}"'))
def orangehrm_should_show_login_error(
    orangehrm_authentication_workflow: AuthenticationWorkflow,
    expected_message: str,
) -> None:
    orangehrm_authentication_workflow.should_reject_login(expected_message)


@when("the user searches the PIM employee list with criteria:", target_fixture="employee_search_context")
def user_searches_pim_employee_list(
    orangehrm_pim_workflow: PimWorkflow,
    signed_in_dashboard_page: DashboardPage,
    datatable: list[list[str]],
) -> EmployeeSearchContext:
    criteria = EmployeeSearchCriteria.from_row(first_data_row(datatable))
    employee_list_page = orangehrm_pim_workflow.search_for_employees(criteria)
    return EmployeeSearchContext(page=employee_list_page, criteria=criteria)


@then("PIM employee results should be displayed")
def pim_employee_results_should_be_displayed(
    orangehrm_pim_workflow: PimWorkflow,
    employee_search_context: EmployeeSearchContext,
) -> None:
    orangehrm_pim_workflow.should_show_employee_results(employee_search_context.page)


@then("the PIM search form should keep the selected criteria")
def pim_search_form_should_keep_selected_criteria(
    orangehrm_pim_workflow: PimWorkflow,
    employee_search_context: EmployeeSearchContext,
) -> None:
    orangehrm_pim_workflow.should_keep_search_criteria(
        employee_search_context.page,
        employee_search_context.criteria,
    )


@when("the user filters leave records with:", target_fixture="leave_filter_context")
def user_filters_leave_records(
    orangehrm_leave_workflow: LeaveWorkflow,
    signed_in_dashboard_page: DashboardPage,
    datatable: list[list[str]],
) -> LeaveFilterContext:
    leave_filter = LeaveFilter.from_row(first_data_row(datatable))
    leave_list_page = orangehrm_leave_workflow.filter_leave_records(leave_filter)
    return LeaveFilterContext(page=leave_list_page, leave_filter=leave_filter)


@then("Leave results should be displayed")
def leave_results_should_be_displayed(
    orangehrm_leave_workflow: LeaveWorkflow,
    leave_filter_context: LeaveFilterContext,
) -> None:
    orangehrm_leave_workflow.should_show_leave_results(leave_filter_context.page)


@then("the Leave filter form should keep the selected criteria")
def leave_filter_form_should_keep_selected_criteria(
    orangehrm_leave_workflow: LeaveWorkflow,
    leave_filter_context: LeaveFilterContext,
) -> None:
    orangehrm_leave_workflow.should_keep_filter_values(
        leave_filter_context.page,
        leave_filter_context.leave_filter,
    )

