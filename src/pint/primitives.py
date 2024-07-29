from collections.abc import Sequence, Sized
from typing import TypeVar

from pint import Error, Parser, ParseResult, Result

T = TypeVar("T", bound=Sized)


def just(expected: T) -> Parser[Sequence[T], T]:
    """Parser which only accepts the given value.

    Args:
        expected (T): The expected value.

    Returns:
        Parser[Sequence[T], T]: A parser which has an input of `Sequence[T]` and an
        output of `T`.

    Examples:
        >>> from pint.primitives import just
        >>> parse_a = just("a")
        >>> assert parse_a.parse("a") == Result("", "a")
    """

    def parser_fn(inp: Sequence[T]) -> "ParseResult[Sequence[T], T]":
        if inp[0 : len(expected)] == expected:
            return Result(inp[len(expected) :], expected)
        return Error("Unexpected character.")

    return Parser(parser_fn)
