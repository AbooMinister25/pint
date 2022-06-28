from pint import ident, symbol, take_while, ParseError


def test_map():
    last_letter = ident().map_to(lambda x: x[-1])

    assert not isinstance(last_letter.parse("hello"), ParseError)
    assert last_letter.parse("hello") == ("", "o")


def test_then():
    assign_parser = (
        ident()
        .padded_whitespace()
        .then(symbol("=").padded_whitespace())
        .then(take_while(lambda c: c.isalnum()).padded_whitespace())
    )

    assert not isinstance(assign_parser.parse("x = 10"), ParseError)
    assert assign_parser.parse("x = 10") == ("", (("x", "="), "10"))


def test_then_ignore():
    name = take_while(lambda c: c.isalpha())
    first_name = name.padded_whitespace().then_ignore(name)

    assert not isinstance(first_name.parse("John Doe"), ParseError)
    assert first_name.parse("John Doe") == ("", "John")


def test_ignore_then():
    name = take_while(lambda c: c.isalpha())
    last_name = name.padded_whitespace().ignore_then(name)

    assert not isinstance(last_name.parse("John Doe"), ParseError)
    assert last_name.parse("John Doe") == ("", "Doe")


def test_one_or_more():
    multiple_a = symbol("a").one_or_more()

    assert not isinstance(multiple_a.parse("aaaa"), ParseError)
    assert multiple_a.parse("aaaa") == ("", ["a", "a", "a", "a"])


def test_zero_or_more():
    any_a = symbol("a").zero_or_more()
    
    assert not isinstance(any_a.parse("aaaa"), ParseError)
    assert any_a.parse("aaaa") == ("", ["a", "a", "a", "a"])
    assert not isinstance(any_a.parse(""), ParseError)