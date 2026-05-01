from functools import partial

from pytest_bdd import given, parsers, scenarios, then


scenarios("parser_examples.feature")

parse_typed = partial(
    parsers.cfparse,
    extra_types={
        "Number": int,
        "Price": float,
    },
)


@then("the parser demo starts")
def parser_demo_starts() -> None:
    assert True


@then(parsers.parse("there are {item_count:d} items in the {section} section"))
def verify_item_count(item_count: int, section: str) -> None:
    assert item_count == 3
    assert section == "cart"


@then(parsers.re(r"I have (?P<count>five|six) products"))
def verify_product_word_count(count: str) -> None:
    assert count in {"five", "six"}


@then(parsers.re(r"the (?P<button>submit|cancel|reset) button is (?P<state>enabled|disabled)"))
def verify_button_state(button: str, state: str) -> None:
    assert button == "submit"
    assert state == "disabled"


@given(
    parse_typed("the order total is {amount:Number}"),
    target_fixture="order_amount",
)
def store_order_total(amount: int) -> int:
    return amount


@then(parse_typed("the user pays {amount:Price}"))
def verify_payment_amount(amount: float) -> None:
    assert amount == 12.50


@then(parse_typed("the stored order total should be {expected:Number}"))
def verify_stored_order_total(order_amount: int, expected: int) -> None:
    assert order_amount == expected
