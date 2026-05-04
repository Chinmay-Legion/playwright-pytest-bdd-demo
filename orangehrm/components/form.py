from playwright.sync_api import Page, expect


class FormComponent:
    """Reusable helpers for OrangeHRM's repeated form controls.

    OrangeHRM uses custom inputs, selects, and autocomplete widgets. This
    component keeps that Playwright detail out of page objects and workflows.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def group(self, label: str):
        return self.page.locator(".oxd-input-group", has=self.page.get_by_text(label, exact=True)).first

    def fill_text(self, label: str, value: str | None) -> None:
        if value is None:
            return

        field = self.group(label).locator("input").first
        field.fill(value)

    def text_value(self, label: str) -> str:
        return self.group(label).locator("input").first.input_value()

    def select_option(self, label: str, value: str | None) -> None:
        if value is None:
            return

        self.group(label).locator(".oxd-select-text").click()
        option = self.page.get_by_role("option", name=value, exact=True)

        if option.count() == 0:
            option = self.page.locator(".oxd-select-dropdown").get_by_text(value, exact=True)

        expect(option.first).to_be_visible()
        option.first.click()

    def selected_text(self, label: str) -> str:
        return self.group(label).locator(".oxd-select-text").inner_text().strip()

    def choose_autocomplete(self, label: str, value: str | None) -> None:
        if value is None:
            return

        field = self.group(label).locator("input").first
        field.fill(value)
        option = self.page.locator(".oxd-autocomplete-dropdown").get_by_text(value, exact=False).first
        expect(option).to_be_visible()
        option.click()

    def assert_text_value(self, label: str, expected: str | None) -> None:
        if expected is None:
            return

        expect(self.group(label).locator("input").first).to_have_value(expected)

    def assert_group_contains(self, label: str, expected: str | None) -> None:
        if expected is None:
            return

        expect(self.group(label)).to_contain_text(expected)
