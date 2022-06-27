from pint import ident, ParseError


def test_map():
    last_letter = ident().map_to(lambda x: x[-1])

    assert not isinstance(last_letter.parse("hello"), ParseError)
    assert last_letter.parse("hello") == ("", "o")
