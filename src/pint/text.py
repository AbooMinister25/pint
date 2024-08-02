import string

from pint.parser import Parser
from pint.primitives import fail, one_of, result, take


def just_str(expected: str) -> Parser[str, str]:
    """Parser which matches the given string.

    Args:
        expected (str): The expected string.

    Returns:
        Parser[str, str]: A parser which has an input of `str` and an
        output of `str`.

    Examples:
        >>> from pint.primitives import just_str
        >>> parse_test = just_str("test")
        >>> assert parse_test.parse("test") == Result("", "test")
    """
    return take(len(expected)).bind(
        lambda c: result(c) if c == expected else fail("Unexpected character."),
    )


def whitespace() -> Parser[str, str]:
    r"""Parses zero or more whitespace characters.

    Returns:
        Parser[str, str]: A parser which has an input of `str` and an
        output of `str`.

    Examples:
        >>> parser = whitespace()
        >>> assert parser.parse("foo") == Result("foo", "")
        >>> assert parser.parse("\t\r\n foo") == Result("foo", "\t\r\n ")
    """
    return one_of(string.whitespace).repeat().collect_str()
