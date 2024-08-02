from pint import Result
from pint.parser import seq
from pint.primitives import just, just_str, one_of


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


def test_seq() -> None:
    parser = seq(just_str("hello"), just_str("and"), just_str("bye"))
    assert parser.parse("helloandbye") == Result("", ["hello", "and", "bye"])
