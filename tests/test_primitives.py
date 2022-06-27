from pint import symbol, ident, ParseError


def test_symbol():
    parse_a = symbol("a")
    assert not isinstance(parse_a.parse("a"), ParseError)


def test_identifier():
    assert not isinstance(ident().parse("hi"), ParseError)
    assert ident().parse("foo") == ("", "foo")
