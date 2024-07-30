from collections.abc import Sequence
from typing import Any, Callable, TypeVar

from pint import Error, Parser, ParseResult, Result, parser

T = TypeVar("T")


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


def fail(message: str) -> Parser[Sequence[Any], Any]:
    """Parser which always fails with the given message.

    Args:
        message (str): The input value.

    Returns:
        Parser[Sequence[Any], Any]: A parser which has an input of `Sequence[Any]` and an
        output of `Any`.
    """

    def parser_fn(_: Sequence[Any]) -> "ParseResult[Sequence[Any], Any]":
        return Error(message)

    return Parser(parser_fn)


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
        if inp[0] == expected:
            return Result(inp[1:], expected)
        return Error("Unexpected item.")

    return Parser(parser_fn)


def just_str(expected: str) -> Parser[Sequence[str], str]:
    """Parser which matches the given string.

    Args:
        expected (str): The expected string.

    Returns:
        Parser[Sequence[str], str]: A parser which has an input of `Sequence[str]` and an
        output of `str`.

    Examples:
        >>> from pint.primitives import just_str
        >>> parse_test = just_str("test")
        >>> assert parse_test.parse("test") == Result("", "test")
    """

    def parser_fn(inp: Sequence[str]) -> "ParseResult[Sequence[str], str]":
        if inp[0 : len(expected)] == expected:
            return Result(inp[len(expected) :], expected)
        return Error("Unexpected character.")

    return Parser(parser_fn)


def one_of(values: Sequence[T]) -> Parser[Sequence[T], T]:
    """Parser that accepts one of the given input values.

    Args:
        values (Sequence[T]): The inputs to accept.

    Returns:
        Parser[Sequence[T], T]: A parser which has an input of `Sequence[T]` and an
        output of `T`.
    """

    def parser_fn(inp: Sequence[T]) -> "ParseResult[Sequence[T], T]":
        if inp[0] in values:
            return Result(inp[1:], inp[0])
        return Error("Unexpected item.")

    return Parser(parser_fn)


def none_of(values: Sequence[T]) -> Parser[Sequence[T], T]:
    """Parser that accepts a value if it is not one of the given input values.

    Args:
        values (Sequence[T]): The inputs to check against.

    Returns:
        Parser[Sequence[T], T]: A parser which has an input of `Sequence[T]` and an
        output of `T`.
    """

    def parser_fn(inp: Sequence[T]) -> "ParseResult[Sequence[T], T]":
        if inp[0] not in values:
            return Result(inp[1:], inp[0])
        return Error("Unexpected item.")

    return Parser(parser_fn)


@parser
def take_any(inp: Sequence[Any]) -> "ParseResult[Sequence[Any], Any]":
    """A parser that accepts any input.

    Args:
        inp (Sequence[Any]): The input to parse.

    Returns:
        ParseResult[Sequence[Any], Any]: The parsed result.
    """
    return Result(inp[1:], inp[0])


def satisfy(pred: Callable[[T], bool]) -> Parser[Sequence[T], T]:
    """A parser which accepts any input which satisfies the given predicate
    function.

    Args:
        pred (Callable[[T], bool]): The predicate function.

    Returns:
        Parser[Sequence[T], T]: The created parser.
    """

    def parser_fn(inp: Sequence[T]) -> "ParseResult[Sequence[T], T]":
        if pred(inp[0]):
            return Result(inp[1:], inp[0])
        return Error("Unexpected item.")

    return Parser(parser_fn)


def take_until(pattern: T) -> Parser[Sequence[T], Sequence[T]]:
    """Parser that accepts any input until the given pattern is reached.

    Args:
        pattern (T): The pattern to check against.

    Returns:
        Parser[Sequence[T], Sequence[T]]: The created parser.
    """

    def parser_fn(inp: Sequence[T]) -> "ParseResult[Sequence[T], Sequence[T]]":
        try:
            location = inp.index(pattern)
            return Result(inp[location:], inp[:location])
        except ValueError:
            return Error("Pattern not in sequence.")

    return Parser(parser_fn)
