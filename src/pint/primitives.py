from collections.abc import Sequence
from typing import Any, Callable, TypeVar

from pint import Error, InputStream, Result
from pint.parser import Parser, ParseResult, parser

T = TypeVar("T")


def result(value: T) -> Parser[Any, T]:
    """Parser which succeeds without consuming any of the input string,
    and returns the passed value `value`.

    Args:
        value (T): The value to return.

    Returns:
        Parser[Any, T]: A parser which has an input of `Any` and an
        output of `T`.

    Examples:
        >>> from pint.primitives import result
        >>> always_a = result("a")
        >>> assert always_a.parse("foo") == Result("foo", "a")
    """

    def parser_fn(inp: InputStream[Any]) -> "ParseResult[Any, T]":
        return Result(inp, value)

    return Parser(parser_fn)


@parser
def zero(_: InputStream[Any]) -> "ParseResult[Any, Any]":
    """Parser which always fails.

    Args:
        _ (InputStream[Any]): The input.

    Returns:
        ParseResult[Any], Any]: The result of the parser.
    """
    return Error("Zero parser.")


def fail(message: str) -> Parser[Any, Any]:
    """Parser which always fails with the given message.

    Args:
        message (str): The input value.

    Returns:
        Parser[Any, Any]: A parser which has an input of `Any` and an
        output of `Any`.
    """

    def parser_fn(_: InputStream[Any]) -> "ParseResult[Any, Any]":
        return Error(message)

    return Parser(parser_fn)


@parser
def take_any(inp: InputStream[Any]) -> "ParseResult[Any, Any]":
    """A parser that accepts any input.

    Args:
        inp (InputStream[Any]): The input to parse.

    Returns:
        ParseResult[Any, Any]: The parsed result.
    """
    try:
        taken, remaining = inp.take(1)
        return Result(remaining, taken)
    except IndexError:
        return Error("Input empty.")


def take(amount: int) -> Parser[Any, Any]:
    """A parser that accepts any input for the given amount.

    Args:
        amount (int): The amount to take.

    Returns:
        Parser[Any, Any]: The created parser.
    """

    def parser_fn(inp: InputStream[Any]) -> "ParseResult[Any, Any]":
        taken, remaining = inp.take(amount)
        return Result(remaining, taken)

    return Parser(parser_fn)


def just(expected: T) -> Parser[T, T]:
    """Parser which only accepts the given value.

    Args:
        expected (T): The expected value.

    Returns:
        Parser[T, T]: A parser which has an input of `Any` and an
        output of `T`.

    Examples:
        >>> from pint.primitives import just
        >>> parse_a = just("a")
        >>> assert parse_a.parse("a") == Result("", "a")
    """
    return take_any().bind(lambda c: result(c) if c == expected else fail(f"Unexpected item {c}"))


def one_of(values: Sequence[T]) -> Parser[T, T]:
    """Parser that accepts one of the given input values.

    Args:
        values (Sequence[T]): The inputs to accept.

    Returns:
        Parser[T, T]: A parser which has an input of `T` and an
        output of `T`.
    """
    return take_any().bind(lambda c: result(c) if c in values else fail("Unexpected item."))


def none_of(values: Sequence[T]) -> Parser[T, T]:
    """Parser that accepts a value if it is not one of the given input values.

    Args:
        values (Sequence[T]): The inputs to check against.

    Returns:
        Parser[T, T]: A parser which has an input of `T` and an
        output of `T`.
    """
    return take_any().bind(lambda c: result(c) if c not in values else fail("Unexpected item."))


def satisfy(pred: Callable[[T], bool]) -> Parser[T, T]:
    """A parser which accepts any input which satisfies the given predicate
    function.

    Args:
        pred (Callable[[T], bool]): The predicate function.

    Returns:
        Parser[T, T]: The created parser.
    """
    return take_any().bind(lambda c: result(c) if pred(c) else fail("Unexpected item."))


def take_until(pattern: T) -> Parser[T, Sequence[T]]:
    """Parser that accepts any input until the given pattern is reached.

    Args:
        pattern (T): The pattern to check against.

    Returns:
        Parser[T, Sequence[T]]: The created parser.
    """

    def parser_fn(inp: InputStream[T]) -> "ParseResult[T, Sequence[T]]":
        try:
            location = inp.index(pattern)
            return take(location).parse(inp)
        except ValueError:
            return Error("Pattern not in sequence.")

    return Parser(parser_fn)
