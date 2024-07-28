from pint import ident, symbol, take_while


def test_symbol() -> None:
    parse_a = symbol("a")
    assert parse_a.parse("a") == ("", "a")


def test_identifier() -> None:
    assert ident().parse("foo") == ("", "foo")
    assert ident().parse("abc123") == ("", "abc123")


def test_take_while() -> None:
    number_parser = take_while(lambda c: c.isnumeric())

    assert number_parser.parse("10") == ("", "10")
    assert number_parser.parse("10 not a number") == (" not a number", "10")
