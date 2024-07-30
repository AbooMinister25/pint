from collections.abc import Sequence, Sized
from typing import Any, TypeVar

from pint import Error, Parser, ParseResult, Result, parser

T = TypeVar("T", bound=Sized)


def result(value: T) -> Parser[Sequence[T], T]:
    """Parser which succeeds without consuming any of the input string,
    and returns the passed value `value`.

    Args:
        value (T): The value to return.

    Returns:
        Parser[Sequence[T], T]: A parser which has an input of `Sequence[T]` and an
        output of `T`.

    Examples:
        >>> from pint.primitives import result
        >>> always_a = result("a")
        >>> assert always_a.parse("foo") == Result("foo", "a")
    """

    def parser_fn(inp: Sequence[T]) -> "ParseResult[Sequence[T], T]":
        return Result(inp, value)

    return Parser(parser_fn)


@parser
def zero(_: Sequence[Any]) -> "ParseResult[Sequence[Any], Any]":
    """Parser which always fails.

    Args:
        _ (Sequence[T]): The input.

    Returns:
        ParseResult[Sequence[T], T]: The result of the parser.
    """
    return Error("Zero parser.")


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
