from __future__ import annotations
from typing import Callable, TypeVar, Optional, Generic
from pint.core import Parser, ParseResult, ParseFunction, ParseError


def symbol(expected: str) -> Parser[None]:
    """Parser which only accepts the expected item.

    Args:
        expected (str): The expected string.

    Returns:
        Parser[None]: A parser which outputs `None`.

    Examples:
        >>> from pint import symbol
        >>> parse_a = symbol("a")
        >>> print(parse_a.parse("a"))
        >>> print(parse_a.parse("b"))
    """

    def parser(inp: str) -> ParseResult[None]:
        if inp[0 : len(expected)] == expected:
            return (inp[len(expected) :], None)
        else:
            return ParseError(inp, f"Expected to find {expected}")

    return Parser(parser)


def ident() -> Parser[str]:
    """Parser which accepts an identifier.

    Returns:
        Parser[str]: A parser which outputs `str`.

    Examples:
        >>> from pint import ident
        >>> print(ident().parse("foo"))
    """

    def parser(inp: str) -> ParseResult[str]:
        ident = ""

        if not inp[0].isidentifier():
            return ParseError(inp, f"Expected an identifier")

        for char in inp:
            if char.isidentifier():
                ident += char
            else:
                break

        return (inp[len(ident) :], ident)

    return Parser(parser)
