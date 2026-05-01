from pytest_bdd import given, parsers, scenarios, then, when
from playwright.sync_api import Page

from pages.pta_table_page import PtaTablePage


scenarios("practice_test_automation_table.feature")


def data_table_to_dicts(datatable: list[list[str]]) -> list[dict[str, str]]:
    headers = datatable[0]
    rows = datatable[1:]
    return [dict(zip(headers, row)) for row in rows]


@given("the user is on the PTA table page", target_fixture="table_page")
def navigate_to_pta_table(page: Page) -> PtaTablePage:
    table_page = PtaTablePage(page)
    table_page.navigate()
    return table_page


@then("the course table should be displayed")
def verify_table_is_displayed(table_page: PtaTablePage) -> None:
    table_page.assert_loaded()


@when(parsers.parse('the user filters the table by language "{language}"'))
def filter_table_by_language(table_page: PtaTablePage, language: str) -> None:
    table_page.select_language(language)


@when(parsers.parse('the user keeps only level "{level}"'))
def keep_only_level(table_page: PtaTablePage, level: str) -> None:
    table_page.keep_only_level(level)


@when(parsers.parse('the user sets minimum enrollments to "{minimum}"'))
def set_minimum_enrollments(table_page: PtaTablePage, minimum: str) -> None:
    table_page.set_min_enrollments(minimum)


@when(parsers.parse('the user sorts the table by "{column_name}"'))
def sort_table_by_column(table_page: PtaTablePage, column_name: str) -> None:
    table_page.sort_by(column_name)


@then(parsers.parse('every visible course should have language "{language}"'))
def verify_visible_courses_have_language(table_page: PtaTablePage, language: str) -> None:
    table_page.assert_every_visible_course_has_language(language)


@then(parsers.parse('every visible course should have level "{level}"'))
def verify_visible_courses_have_level(table_page: PtaTablePage, level: str) -> None:
    table_page.assert_every_visible_course_has_level(level)


@then(parsers.parse("every visible course should have at least {minimum:d} enrollments"))
def verify_visible_courses_have_minimum_enrollments(table_page: PtaTablePage, minimum: int) -> None:
    table_page.assert_every_visible_course_has_min_enrollments(minimum)


@then("enrollments should be sorted from lowest to highest")
def verify_enrollments_are_sorted(table_page: PtaTablePage) -> None:
    table_page.assert_enrollments_sorted_ascending()


@then("the table should contain these courses:")
def verify_table_contains_courses(table_page: PtaTablePage, datatable: list[list[str]]) -> None:
    table_page.assert_course_values(data_table_to_dicts(datatable))
