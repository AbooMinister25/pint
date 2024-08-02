from pint import Result
from pint.text import just_str


def test_just_str() -> None:
    parse_test = just_str("test")
    assert parse_test.parse("test") == Result("", "test")
