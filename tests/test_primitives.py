from pint import symbol, ident, ParseError


def test_symbol():
    parse_a = symbol("a")
    assert parse_a.parse("a") != ParseError


def test_identifier():
    assert ident().parse("hi") != ParseError
    assert ident().parse("foo") == ("", "foo")
