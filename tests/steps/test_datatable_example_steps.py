from pytest_bdd import given, parsers, scenarios, then


scenarios("datatable_examples.feature")


def data_table_to_dicts(datatable: list[list[str]]) -> list[dict[str, str]]:
    headers = datatable[0]
    rows = datatable[1:]
    return [dict(zip(headers, row)) for row in rows]


@given("these product names:", target_fixture="product_names")
def store_product_names(datatable: list[list[str]]) -> list[str]:
    product_rows = data_table_to_dicts(datatable)
    return [row["product_name"] for row in product_rows]


@then(parsers.parse("the product list should contain {expected_count:d} products"))
def verify_product_count(product_names: list[str], expected_count: int) -> None:
    assert len(product_names) == expected_count


@then(parsers.parse('the product list should include "{expected_product}"'))
def verify_product_is_present(product_names: list[str], expected_product: str) -> None:
    assert expected_product in product_names


@given("these checkout settings:", target_fixture="checkout_settings")
def store_checkout_settings(datatable: list[list[str]]) -> dict[str, str]:
    setting_rows = data_table_to_dicts(datatable)
    return {row["field"]: row["value"] for row in setting_rows}


@then(parsers.parse('the checkout setting "{field}" should be "{expected_value}"'))
def verify_checkout_setting(checkout_settings: dict[str, str], field: str, expected_value: str) -> None:
    assert checkout_settings[field] == expected_value


@given("these course records:", target_fixture="course_records")
def store_course_records(datatable: list[list[str]]) -> list[dict[str, str]]:
    return data_table_to_dicts(datatable)


@then(parsers.parse('there should be {expected_count:d} courses with language "{language}"'))
def verify_course_language_count(course_records: list[dict[str, str]], expected_count: int, language: str) -> None:
    matching_courses = [course for course in course_records if course["language"] == language]
    assert len(matching_courses) == expected_count


@then(parsers.parse('the most popular course should be "{expected_course}"'))
def verify_most_popular_course(course_records: list[dict[str, str]], expected_course: str) -> None:
    most_popular_course = max(course_records, key=lambda course: int(course["enrollments"]))
    assert most_popular_course["course_name"] == expected_course


@given("these visible table rows:", target_fixture="visible_rows")
def store_visible_rows(datatable: list[list[str]]) -> list[dict[str, str]]:
    return data_table_to_dicts(datatable)


@then("the rows should match exactly:")
def verify_rows_match_exactly(visible_rows: list[dict[str, str]], datatable: list[list[str]]) -> None:
    assert visible_rows == data_table_to_dicts(datatable)
