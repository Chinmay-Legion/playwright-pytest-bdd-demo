from dataclasses import dataclass

from orangehrm.models.leave import LeaveFilter
from orangehrm.models.pim import EmployeeSearchCriteria
from orangehrm.pages.employee_list_page import EmployeeListPage
from orangehrm.pages.leave_list_page import LeaveListPage


def data_table_to_dicts(datatable: list[list[str]]) -> list[dict[str, str]]:
    """Convert a pytest-bdd data table into row dictionaries."""

    headers = datatable[0]
    return [dict(zip(headers, row)) for row in datatable[1:]]


def first_data_row(datatable: list[list[str]]) -> dict[str, str]:
    """Return the first business-data row from a BDD data table."""

    return data_table_to_dicts(datatable)[0]


@dataclass(frozen=True)
class EmployeeSearchContext:
    """State shared between PIM When and Then steps."""

    page: EmployeeListPage
    criteria: EmployeeSearchCriteria


@dataclass(frozen=True)
class LeaveFilterContext:
    """State shared between Leave When and Then steps."""

    page: LeaveListPage
    leave_filter: LeaveFilter

