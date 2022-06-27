from pint import ident, symbol, take_while, ParseError


def test_map():
    last_letter = ident().map_to(lambda x: x[-1])

    assert not isinstance(last_letter.parse("hello"), ParseError)
    assert last_letter.parse("hello") == ("", "o")


def test_then():
    assign_parser = ident().then(symbol("=")).then(take_while(lambda c: c.isalnum()))

    assert not isinstance(assign_parser.parse("x = 10"), ParseError)
    assert assign_parser.parse("x = 10") == ("", (("x", "="), "10"))
