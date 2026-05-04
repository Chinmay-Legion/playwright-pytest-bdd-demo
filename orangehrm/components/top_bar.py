from playwright.sync_api import Page, expect


class TopBar:
    """Top navigation and user menu shared by OrangeHRM pages."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.module_title = page.locator(".oxd-topbar-header-breadcrumb-module")
        self.user_menu = page.locator(".oxd-userdropdown-tab")

    def assert_module(self, module_name: str) -> None:
        expect(self.module_title).to_have_text(module_name)

    def assert_user_menu_available(self) -> None:
        expect(self.user_menu).to_be_visible()

    def logout(self) -> None:
        self.user_menu.click()
        self.page.get_by_role("menuitem", name="Logout").click()

