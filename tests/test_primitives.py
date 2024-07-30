from pint import Error, Result
from pint.primitives import just, result, zero


def test_result() -> None:
    always_a = result("a")
    assert always_a.parse("foo") == Result("foo", "a")


def test_zero() -> None:
    parser = zero()
    assert parser.parse("test") == Error("Zero parser.")


def test_just() -> None:
    parse_a = just("a")
    assert parse_a.parse("a") == Result("", "a")
