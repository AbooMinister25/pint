from pint import Error, Result
from pint.primitives import just, one_of


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


def test_collect_str() -> None:
    number = one_of("0123456789").repeat().collect_str()
    assert number.parse("532") == Result("", "532")
    assert number.map(int).parse("532") == Result("", 532)


def test_fold() -> None:
    number = one_of("0123456789").map(int)
    addition = number.then(just("+").ignore_then(number).repeat()).fold(lambda a, b: a + b)
    assert addition.parse("5+5") == Result("", 10)


def test_optional() -> None:
    parser = just("-").optional().then(one_of("0123456789").repeat().collect_str())
    assert parser.parse("-10") == Result("", ("-", "10"))
    assert parser.parse("10") == Result("", (None, "10"))
