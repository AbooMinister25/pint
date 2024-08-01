"""A user friendly parser combinator library for python."""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar

import pint.primitives
from pint import Error, Input, Output, ParseFunction, ParseResult, Result

if TYPE_CHECKING:
    from collections.abc import Sequence

BindOutput = TypeVar("BindOutput")
MappedOutput = TypeVar("MappedOutput")
ThenOutput = TypeVar("ThenOutput")
DO1 = TypeVar("DO1")
DO2 = TypeVar("DO2")


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

    def alt(self, other: Parser[Input, Output]) -> Parser[Input, Output]:
        """Returns a parser that invokes this parser, and on failure, invokes
        `other`.

        If `self` parses successfully, then its output is returned and `other` isn't
        invoked. If both parsers fail, a combined error message with the failures of
        both parsers is returned.

        Args:
            other (Parser[Input, Output]): The other parser to use.

        Returns:
            Parser[Input, Output]: A parser which takes `Input` and returns `Output`.

        Examples:
            >>> underscore_or_number = just("_").alt(one_of("0123456789"))
            >>> assert underscore_or_number.parse("_") == Result("", "_")
            >>> assert underscore_or_number.parse("1") == Result("", "1")
        """

        def parser_fn(inp: Sequence[Input]) -> ParseResult[Sequence[Input], Output]:
            result = self.parse(inp)
            if isinstance(result, Result):
                return result

            other_result = other.parse(inp)
            if isinstance(other_result, Error):
                message = f"Both parsers returned an error. \
                    First parser: {result.message}; Second parser: {other_result.message}"
                return Error(message)

            return other_result

        return Parser(parser_fn)

    def repeat(
        self,
        minimum: int = 0,
        maximum: Optional[int] = None,
    ) -> Parser[Input, list[Output]]:
        """Repeats this parser at least `minimum` times, and at most `maximum` times.

        This returns a parser with all the outputs gathered in a list.

        Args:
            minimum (int, optional): The minimum number of times to parse. Defaults to 0.
            maximum (Optional[int], optional): The maximum number of times to parse. Defaults
            to None.

        Returns:
            Parser[Input, list[Output]]: A parser which outputs a list of all the outputs
            generated.

        Examples:
        >>> digits = one_of("0123456789").repeat()
        >>> assert digits.parse("123") == Result("", ["1", "2", "3"])
        >>> two_digits = one_of("0123456789").repeat(maximum=2)
        >>> assert two_digits.parse("123") == Result("3", ["1", "2"])
        >>> at_least_one = one_of("0123456789").repeat(minimum=1)
        >>> assert at_least_one.parse("") == Error("Expected input.")
        >>> at_least_two = one_of("0123456789").repeat(minimum=2)
        >>> assert at_least_two.parse("1") == Error("Expected input.")
        >>> assert at_least_two.parse("123") == Result("", ["1", "2", "3"])
        >>> between_two_and_four = one_of("0123456789").repeat(minimum=2, maximum=4)
        >>> assert between_two_and_four.parse("1") == Error("Expected input.")
        >>> assert between_two_and_four.parse("123") == Result("", ["1", "2", "3"])
        >>> assert between_two_and_four.parse("1234") == Result("", ["1", "2", "3", "4"])
        >>> assert between_two_and_four.parse("12345") == Result("5", ["1", "2", "3", "4"])

        """

        def parser_fn(inp: Sequence[Input]) -> ParseResult[Sequence[Input], list[Output]]:
            results: list[Output] = []

            while True:
                result = self.parse(inp)
                if isinstance(result, Error):
                    break

                results.append(result.output)
                inp = result.input

                if maximum and len(results) == maximum:
                    break

            if len(results) < minimum:
                return Error("Expected input.")

            return Result(inp, results)

        return Parser(parser_fn)

    def delimited(
        self,
        start: Parser[Input, DO1],
        end: Parser[Input, DO2],
    ) -> Parser[Input, Output]:
        """Return a parser which delimits this parser with two other parsers.

        The parser `start` is invoked, its output is ignored, then this parser
        is invoked, and then parser `end` is invoked, and its out is ignored.

        This is equivalent to `start.ignore_then(self).then_ignore(end)`.

        Args:
            start (Parser[Input, DO1]): The parser which precedes this one.
            end (Parser[Input, DO2]): The parser which follows this one.

        Returns:
            Parser[Input, Output]: The generated parser.

        Examples:
            >>> delim_parens = one_of("0123456789").delimited(just("("), just(")"))
            >>> assert delim_parens.parse("(1)") == Result("", "1")
        """
        return start.ignore_then(self).then_ignore(end)


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
