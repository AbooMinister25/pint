from pint.parser import Parser
from pint.primitives import fail, result, take


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
