from dataclasses import dataclass


@dataclass(frozen=True)
class EmployeeSearchCriteria:
    """Search fields supported by the PIM employee list demo."""

    employee_name: str | None = None
    employee_id: str | None = None
    employment_status: str | None = None
    include: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "EmployeeSearchCriteria":
        return cls(
            employee_name=row.get("employee_name") or None,
            employee_id=row.get("employee_id") or None,
            employment_status=row.get("employment_status") or None,
            include=row.get("include") or None,
        )

