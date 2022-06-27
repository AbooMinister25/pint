from pint import symbol, ident, take_while, ParseError


def test_symbol():
    parse_a = symbol("a")
    assert not isinstance(parse_a.parse("a"), ParseError)
    assert parse_a.parse("a") == ("", "a")


def test_identifier():
    assert not isinstance(ident().parse("hi"), ParseError)
    assert ident().parse("foo") == ("", "foo")


def test_take_while():
    number_parser = take_while(lambda c: c.isnumeric())

    assert not isinstance(number_parser.parse("10"), ParseError)
    assert number_parser.parse("10") == ("", "10")
    assert number_parser.parse("10 not a number") == (" not a number", "10")
