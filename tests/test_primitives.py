from pint import Result
from pint.primitives import just


def test_just() -> None:
    parse_a = just("a")
    assert parse_a.parse("a") == Result("", "a")
