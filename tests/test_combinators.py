from pint import Error, Result
from pint.primitives import just, one_of


def test_map() -> None:
    digits = one_of("0123456789").map(lambda i: int(i))
    assert digits.parse("1") == Result("", 1)


def test_then() -> None:
    a_and_num = just("a").then(one_of("0123456789"))
    assert a_and_num.parse("a1") == Result("", ("a", "1"))


def test_then_ignore() -> None:
    ignore_underscore = one_of("0123456789").then_ignore(just("_"))
    assert ignore_underscore.parse("2_") == Result("", "2")


def test_ignore_then() -> None:
    ignore_underscore = just("_").ignore_then(one_of("0123456789"))
    assert ignore_underscore.parse("_2") == Result("", "2")


def test_repeat() -> None:
    digits = one_of("0123456789").repeat()
    assert digits.parse("123") == Result("", ["1", "2", "3"])
    two_digits = one_of("0123456789").repeat(maximum=2)
    assert two_digits.parse("123") == Result("3", ["1", "2"])
    at_least_one = one_of("0123456789").repeat(minimum=1)
    assert at_least_one.parse("") == Error("Expected input.")
    at_least_two = one_of("0123456789").repeat(minimum=2)
    assert at_least_two.parse("1") == Error("Expected input.")
    assert at_least_two.parse("123") == Result("", ["1", "2", "3"])
    between_two_and_four = one_of("0123456789").repeat(minimum=2, maximum=4)
    assert between_two_and_four.parse("1") == Error("Expected input.")
    assert between_two_and_four.parse("123") == Result("", ["1", "2", "3"])
    assert between_two_and_four.parse("1234") == Result("", ["1", "2", "3", "4"])
    assert between_two_and_four.parse("12345") == Result("5", ["1", "2", "3", "4"])


def test_delimited() -> None:
    delim_parens = one_of("0123456789").delimited(just("("), just(")"))
    assert delim_parens.parse("(1)") == Result("", "1")


def test_alt() -> None:
    underscore_or_number = just("_").alt(one_of("0123456789"))
    assert underscore_or_number.parse("_") == Result("", "_")
    assert underscore_or_number.parse("1") == Result("", "1")
    operator = just("+").alt(just("-")).alt(just("*")).alt(just("/"))
    assert operator.parse("*") == Result("", "*")
    assert operator.parse("-") == Result("", "-")
    assert operator.parse("/") == Result("", "/")
    assert operator.parse("+") == Result("", "+")
