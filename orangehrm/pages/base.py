from playwright.sync_api import Page


class OrangeHrmBasePage:
    """Base page for OrangeHRM page objects."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def goto_path(self, path: str) -> None:
        self.page.goto(f"{self.base_url}/{path.lstrip('/')}")

