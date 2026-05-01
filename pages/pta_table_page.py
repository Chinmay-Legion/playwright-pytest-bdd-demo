from playwright.sync_api import Page, expect

from pages.base_page import BasePage

_URL = "https://practicetestautomation.com/practice-test-table/"


class PtaTablePage(BasePage):
    COLUMN_INDEX = {
        "ID": 0,
        "Course Name": 1,
        "Language": 2,
        "Level": 3,
        "Enrollments": 4,
        "Link": 5,
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Test Table")
        self.table = page.locator("table").filter(has_text="Course Name")

    def navigate(self) -> None:
        super().navigate(_URL)

    def assert_loaded(self) -> None:
        expect(self.heading).to_be_visible()
        expect(self.table).to_be_visible()

    def select_language(self, language: str) -> None:
        self.page.get_by_label(language, exact=True).check()

    def keep_only_level(self, level: str) -> None:
        for level_name in ["Beginner", "Intermediate", "Advanced"]:
            checkbox = self.page.get_by_label(level_name, exact=True)

            if level_name == level:
                checkbox.check()
            else:
                checkbox.uncheck()

    def set_min_enrollments(self, minimum: str) -> None:
        self.page.get_by_label("Minimum enrollments").select_option(label=minimum)

    def sort_by(self, column_name: str) -> None:
        self.page.get_by_label("Sort by:").select_option(label=column_name)

    def visible_course_rows(self):
        return self.table.locator("tbody tr").filter(visible=True)

    def course_row(self, course_name: str):
        return self.visible_course_rows().filter(has_text=course_name).first

    def course_cell_text(self, course_name: str, column_name: str) -> str:
        column_index = self.COLUMN_INDEX[column_name]
        return self.course_row(course_name).locator("td").nth(column_index).inner_text().strip()

    def visible_column_values(self, column_name: str) -> list[str]:
        column_index = self.COLUMN_INDEX[column_name]
        rows = self.visible_course_rows()
        return [rows.nth(index).locator("td").nth(column_index).inner_text().strip() for index in range(rows.count())]

    def visible_enrollments(self) -> list[int]:
        return [int(value.replace(",", "")) for value in self.visible_column_values("Enrollments")]

    def assert_every_visible_course_has_language(self, language: str) -> None:
        languages = self.visible_column_values("Language")
        assert languages
        assert all(value == language for value in languages)

    def assert_every_visible_course_has_level(self, level: str) -> None:
        levels = self.visible_column_values("Level")
        assert levels
        assert all(value == level for value in levels)

    def assert_every_visible_course_has_min_enrollments(self, minimum: int) -> None:
        enrollments = self.visible_enrollments()
        assert enrollments
        assert all(value >= minimum for value in enrollments)

    def assert_enrollments_sorted_ascending(self) -> None:
        enrollments = self.visible_enrollments()
        assert enrollments == sorted(enrollments)

    def assert_course_values(self, expected_courses: list[dict[str, str]]) -> None:
        for expected_course in expected_courses:
            course_name = expected_course["course_name"]

            expect(self.course_row(course_name)).to_be_visible()
            assert self.course_cell_text(course_name, "Language") == expected_course["language"]
            assert self.course_cell_text(course_name, "Level") == expected_course["level"]
            assert self.course_cell_text(course_name, "Enrollments") == expected_course["enrollments"]
