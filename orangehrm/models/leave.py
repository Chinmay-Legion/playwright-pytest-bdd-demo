from dataclasses import dataclass


@dataclass(frozen=True)
class LeaveFilter:
    """Search fields supported by the Leave list demo."""

    from_date: str | None = None
    to_date: str | None = None
    status: str | None = None
    leave_type: str | None = None
    employee_name: str | None = None
    sub_unit: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "LeaveFilter":
        return cls(
            from_date=row.get("from_date") or None,
            to_date=row.get("to_date") or None,
            status=row.get("status") or None,
            leave_type=row.get("leave_type") or None,
            employee_name=row.get("employee_name") or None,
            sub_unit=row.get("sub_unit") or None,
        )

