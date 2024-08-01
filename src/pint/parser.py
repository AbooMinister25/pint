"""A user friendly parser combinator library for python."""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

import pint.primitives
from pint import Error, Input, Output, ParseFunction, ParseResult

if TYPE_CHECKING:
    from collections.abc import Sequence

BindOutput = TypeVar("BindOutput")
MappedOutput = TypeVar("MappedOutput")


class Parser(Generic[Input, Output]):
    """Wraps a parser function and implements combinators.

    Attributes:
        parser_fn (ParseFunction[Sequence[Input], Output]): The wrapped parsing function.
    """

    def __init__(self, parser_fn: ParseFunction[Sequence[Input], Output]) -> None:
        """Creates a new Parser with the given parser function.

        Args:
            parser_fn (ParseFunction[Sequence[Input], Output]): The parsing function to wrap.
        """
        self.parser_fn = parser_fn

    def parse(self, inp: Sequence[Input]) -> ParseResult[Sequence[Input], Output]:
        """Parse the given input with the wrapped parser_fn.

        Args:
            inp (Sequence[Input]): The input to parse.

        Returns:
            ParseResult[Sequence[Input], Output]: The parsed result.
        """
        return self.parser_fn(inp)

    def bind(
        self,
        binder: Callable[[Output], Parser[Input, BindOutput]],
    ) -> Parser[Input, BindOutput]:
        """Binds this parser into another with a binder function.

        `binder` is a function which takes the output of this parser as its only argument
        and returns a new `Parser[Input, BindOutput]`.

        Args:
            binder (Callable[[Output], Parser[Input, BindOutput]]): The binder function.

        Returns:
            Parser[Input, BindOutput]: The new bound parser.
        """

        def parser_fn(inp: Sequence[Input]) -> ParseResult[Sequence[Input], BindOutput]:
            result = self.parse(inp)
            if isinstance(result, Error):
                return result

            bound_parser = binder(result.output)
            return bound_parser.parse(result.input)

        return Parser(parser_fn)

    def map(self, map_fn: Callable[[Output], MappedOutput]) -> Parser[Input, MappedOutput]:
        """Maps the output of this parser to another value.

        Args:
            map_fn (Callable[[Output], MappedOutput]): The function to call on the
            output of this parser.

        Returns:
            Parser[Input, MappedOutput]: The new mapped parser.

        Examples:
            >>> from pint import Result
            >>> from pint.primitives import one_of
            >>> digits = one_of("0123456789").map(lambda i: int(i))
            >>> assert digits.parse("1") == Result("", 1)
        """
        return self.bind(lambda res: pint.primitives.result(map_fn(res)))


def parser(parse_fn: ParseFunction[Sequence[Input], Output]) -> Callable[[], Parser[Input, Output]]:
    """A decorator that creates a parser from the given function.

    Args:
        parse_fn (ParseFunction[Sequence[Input], Output]): The parsing function to wrap.

    Returns:
        Callable[[], Parser[Input, Output]]: A function which returns the created parser.
    """

    @wraps(parse_fn)
    def wrapped() -> Parser[Input, Output]:
        return Parser(parse_fn)

    return wrapped
