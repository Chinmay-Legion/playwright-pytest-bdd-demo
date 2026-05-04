from dataclasses import dataclass


@dataclass(frozen=True)
class OrangeHrmUser:
    """Credentials for an OrangeHRM user.

    A dataclass keeps test data explicit and easy to pass through pytest
    fixtures, workflows, and services without using loose dictionaries.
    """

    username: str
    password: str
    display_name: str | None = None

    @classmethod
    def demo_admin(cls) -> "OrangeHrmUser":
        return cls(username="Admin", password="admin123", display_name="Admin")

