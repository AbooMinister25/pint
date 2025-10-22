from pint import Result
from pint.text import just_str, whitespace


def test_just_str() -> None:
    parse_test = just_str("test")
    assert parse_test.parse("test") == Result("", "test")


def test_whitespace() -> None:
    parser = whitespace()
    assert parser.parse("foo") == Result("foo", "")
    assert parser.parse("\t\r\n foo") == Result("foo", "\t\r\n ")
