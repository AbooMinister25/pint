from pint import ident, symbol, take_while


def test_map() -> None:
    last_letter = ident().map_to(lambda x: x[-1])

    assert last_letter.parse("hello") == ("", "o")


def test_then() -> None:
    assign_parser = (
        ident()
        .padded_whitespace()
        .then(symbol("=").padded_whitespace())
        .then(take_while(lambda c: c.isalnum()).padded_whitespace())
    )

    assert assign_parser.parse("x = 10") == ("", (("x", "="), "10"))


def test_then_ignore() -> None:
    name = take_while(lambda c: c.isalpha())
    first_name = name.padded_whitespace().then_ignore(name)

    assert first_name.parse("John Doe") == ("", "John")


def test_ignore_then() -> None:
    name = take_while(lambda c: c.isalpha())
    last_name = name.padded_whitespace().ignore_then(name)

    assert last_name.parse("John Doe") == ("", "Doe")


def test_one_or_more() -> None:
    multiple_a = symbol("a").one_or_more()

    assert multiple_a.parse("aaaa") == ("", ["a", "a", "a", "a"])


def test_zero_or_more() -> None:
    any_a = symbol("a").zero_or_more()

    assert any_a.parse("aaaa") == ("", ["a", "a", "a", "a"])
    assert any_a.parse("") == ("", [])
