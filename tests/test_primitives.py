from pint import symbol, ParseError


def test_symbol():
    parse_a = symbol("a")
    assert parse_a.parse("a") != ParseError
