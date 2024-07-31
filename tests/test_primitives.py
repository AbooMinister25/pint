from pint import Result
from pint.parser import Error
from pint.primitives import (
    fail,
    just,
    just_str,
    none_of,
    one_of,
    result,
    satisfy,
    take,
    take_any,
    take_until,
    zero,
)


def test_result() -> None:
    always_a = result("a")
    assert always_a.parse("foo") == Result("foo", "a")


def test_zero() -> None:
    parser = zero()
    assert parser.parse("test") == Error("Zero parser.")


def test_fail() -> None:
    parser = fail("Oh no.")
    assert parser.parse("test") == Error("Oh no.")


def test_just() -> None:
    parse_a = just("a")
    assert parse_a.parse("a") == Result("", "a")
    assert just("f").parse("foo") == Result("oo", "f")


def test_just_str() -> None:
    parse_test = just_str("test")
    assert parse_test.parse("test") == Result("", "test")


def test_one_of() -> None:
    digits = one_of("123456789")
    assert digits.parse("5") == Result("", "5")
    assert digits.parse("0") == Error("Unexpected item.")


def test_none_of() -> None:
    none = none_of("abc")
    assert none.parse("x") == Result("", "x")
    assert none.parse("a") == Error("Unexpected item.")


def test_take_any() -> None:
    parser = take_any()
    assert parser.parse("a") == Result("", "a")


def test_take() -> None:
    parser = take(5)
    assert parser.parse("hellotheworld") == Result("theworld", "hello")


def test_satisfy() -> None:
    def pred(i: str) -> bool:
        return i.isdigit()

    parser = satisfy(pred)
    assert parser.parse("1") == Result("", "1")
    assert parser.parse("1000") == Result("000", "1")


def test_take_until() -> None:
    parser = take_until("!")
    assert parser.parse("hello!world") == Result("!world", "hello")

    parser = take_until([1, 2])
    assert parser.parse([[1, 2, 3], [1, 2], [1, 2, 3]]) == Result([[1, 2], [1, 2, 3]], [[1, 2, 3]])
