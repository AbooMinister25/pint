from pint import Result
from pint.primitives import just, one_of


def test_map() -> None:
    digits = one_of("0123456789").map(lambda i: int(i))
    assert digits.parse("1") == Result("", 1)


def test_then() -> None:
    a_and_num = just("a").then(one_of("0123456789"))
    assert a_and_num.parse("a1") == Result("", ("a", "1"))
