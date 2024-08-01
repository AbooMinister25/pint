"""A user friendly parser combinator library for python."""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

import pint.primitives
from pint import Error, Input, Output, ParseFunction, ParseResult, Result

if TYPE_CHECKING:
    from collections.abc import Sequence

BindOutput = TypeVar("BindOutput")
MappedOutput = TypeVar("MappedOutput")
ThenOutput = TypeVar("ThenOutput")


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

    def then(self, then_p: Parser[Input, ThenOutput]) -> Parser[Input, tuple[Output, ThenOutput]]:
        """Chains this parser with another one, returning
        a parser which returns the outputs of both parsers in a tuple.

        Args:
            then_p (Parser[Input, ThenOutput]): The parser to chain with this one.

        Returns:
            Parser[Input, tuple[Output, ThenOutput]]: A parser which returns a tuple of the
            output of this parser and the output of the next one.

        Examples:
            >>> from pint import Result
            >>> from pint.primitives import just, one_of
            >>> a_and_num = just("a").then(one_of("0123456789"))
            >>> assert a_and_num.parse("a1") == Result("", ("a", "1"))
        """

        def inner(value: Output) -> Parser[Input, tuple[Output, ThenOutput]]:
            def parser_fn(
                inp: Sequence[Input],
            ) -> ParseResult[Sequence[Input], tuple[Output, ThenOutput]]:
                result = then_p.parse(inp)
                if isinstance(result, Error):
                    return result

                return Result(result.input, (value, result.output))

            return Parser(parser_fn)

        return self.bind(lambda res: inner(res))

    def then_ignore(self, then_p: Parser[Input, ThenOutput]) -> Parser[Input, Output]:
        """Chains this parser with another one, but only returns the output
        of this parser.

        Args:
            then_p (Parser[Input, ThenOutput]): The parser to chain with this one.

        Returns:
            Parser[Input, Output]: A parser which returns the output of this parser.

        Examples:
            >>> from pint import Result
            >>> from pint.primitives import just, one_of
            >>> ignore_underscore = one_of("0123456789").then_ignore(just("_"))
            >>> assert ignore_underscore.parse("2_") == Result("", "2")
        """
        return self.then(then_p).map(lambda r: r[0])

    def ignore_then(self, then_p: Parser[Input, ThenOutput]) -> Parser[Input, ThenOutput]:
        """Chains this parser with another one, but only returns the output
        of the other parser.

        Args:
            then_p (Parser[Input, ThenOutput]): The parser to chain with this one.

        Returns:
            Parser[Input, ThenOutput]: A parser which returns the output of the
            passed `then_p` parser.

        Examples:
            >>> from pint import Result
            >>> from pint.primitives import just, one_of
            >>> ignore_underscore = just("_").ignore_then(one_of("0123456789"))
            >>> assert ignore_underscore.parse("_2") == Result("", "2")
        """
        return self.bind(lambda _: then_p)


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
