from pint import Result
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
