import re

from playwright.sync_api import Page


class SideNavigation:
    """Left navigation shared by OrangeHRM modules."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open_module(self, module_name: str) -> None:
        link_name = re.compile(rf"^\s*{re.escape(module_name)}\s*$", re.IGNORECASE)
        self.page.get_by_role("link", name=link_name).click()

