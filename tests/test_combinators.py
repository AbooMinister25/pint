from pint import Result
from pint.primitives import one_of


def test_map() -> None:
    digits = one_of("0123456789").map(lambda i: int(i))
    assert digits.parse("1") == Result("", 1)
