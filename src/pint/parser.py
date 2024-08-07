"""A user friendly parser combinator library for python."""

from __future__ import annotations

import functools
from functools import wraps
from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar

from pint import Error, Input, InputStream, Output, ParseFunction, ParseResult, Result

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

BindOutput = TypeVar("BindOutput")
MappedOutput = TypeVar("MappedOutput")
ThenOutput = TypeVar("ThenOutput")
DO1 = TypeVar("DO1")
DO2 = TypeVar("DO2")
FoldA = TypeVar("FoldA")
FoldB = TypeVar("FoldB")
PadOutput = TypeVar("PadOutput")


class Parser(Generic[Input, Output]):
    """Wraps a parser function and implements combinators.

    Attributes:
        parser_fn (ParseFunction[Input, Output]): The wrapped parsing function.
    """

    def __init__(self, parser_fn: ParseFunction[Input, Output]) -> None:
        """Creates a new Parser with the given parser function.

        Args:
            parser_fn (ParseFunction[Input, Output]): The parsing function to wrap.
        """
        self.parser_fn = parser_fn

    def parse(self, inp: InputStream[Input] | Sequence[Input]) -> ParseResult[Input, Output]:
        """Parse the given input with the wrapped parser_fn.

        Args:
            inp (InputStream[Input] | Sequence[Input]): The input to parse.

        Returns:
            ParseResult[Input, Output]: The parsed result.
        """
        if not isinstance(inp, InputStream):
            inp = InputStream(inp)

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

        def parser_fn(inp: InputStream[Input]) -> ParseResult[Input, BindOutput]:
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
        return self.bind(lambda res: Parser(lambda inp: Result(inp, map_fn(res))))

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
                inp: InputStream[Input],
            ) -> ParseResult[Input, tuple[Output, ThenOutput]]:
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

        def parser_fn(inp: InputStream[Input]) -> ParseResult[Input, Output]:
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

        def parser_fn(inp: InputStream[Input]) -> ParseResult[Input, list[Output]]:
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

    def fold(
        self: Parser[Input, tuple[FoldA, list[FoldB]]],
        fold_fn: Callable[[FoldA, FoldB], FoldA],
    ) -> Parser[Input, FoldA]:
        """Performs a left fold on the output of this parser.

        This function will only work when the output of this parser is a
        tuple in the form of `tuple[FoldA, list[FoldB]]`.

        Args:
            fold_fn (Callable[[FoldA, FoldB], FoldA]): The function to use to combine
            the outputs.

        Returns:
            Parser[Input, FoldA]: A parser which has an output of `FoldA`.

        Examples:
            >>> number = one_of("0123456789").map(int)
            >>> addition = number.then(just("+").ignore_then(number).repeat()).fold(
            >>> lambda a, b: a + b)
            >>> assert addition.parse("5+5") == Result("", 10)
        """
        return self.map(lambda t: functools.reduce(fold_fn, t[1], t[0]))

    def optional(self) -> Parser[Input, Optional[Output]]:
        """Makes this parser optional.

        Returns `None` if this parser returns an error.

        Returns:
            Parser[Input, Optional[Output]]: A parser which outputs `Output | None`.
        """

        def parser_fn(inp: InputStream[Input]) -> ParseResult[Input, Optional[Output]]:
            result = self.parse(inp)
            return Result(inp, None) if isinstance(result, Error) else result

        return Parser(parser_fn)

    def padded(self, padding: Parser[Input, PadOutput]) -> Parser[Input, Output]:
        """Pads this parser on either side with the given parser.

        This returns a parser which accepts `padding` either preceding or following
        the input.

        Args:
            padding (Parser[Input, PadOutput]): The parser to look for on either side
            of this one.

        Returns:
            Parser[Input, Output]: A parser which returns `Output`.
        """
        return self.delimited(padding.optional(), padding.optional())

    def collect_str(self: Parser[Input, list[str]]) -> Parser[Input, str]:
        """Collects the result of this parser into a string.

        This function is called when the output of this parser is a list
        of strings, and needs to be collected into a single string.

        Returns:
            Parser[Input, str]: A parser which returns a string.

        Examples:
            >>> number = one_of("0123456789").repeat().collect_str()
            >>> assert number.parse("532") == Result("", "532")
            >>> assert number.map(int).parse("532") == Result("", 532)
        """
        return self.map(lambda s: "".join(s))


def seq(*parsers: Parser[Input, object]) -> Parser[Input, list[object]]:
    """Chain the passed parsers and return a list of all their outputs.

    This can be used in place of `Parser.then` to avoid the nested tuples
    that occur from repeatedly chaining it.

    Returns:
        Parser[Input, list[object]]: A parser which returns a list of the
        outputs of the chained parsers.

    Examples:
        >>> parser = seq(just_str("hello"), just_str("and"), just_str("bye"))
        >>> assert parser.parse("helloandbye") == Result("", ["hello", "and", "bye"])
    """

    def parser_fn(inp: InputStream[Input]) -> ParseResult[Input, list[object]]:
        results: list[object] = []
        for parser in parsers:
            result = parser.parse(inp)
            if isinstance(result, Error):
                return result
            results.append(result[1])
            inp = result[0]

        return Result(inp, results)

    return Parser(parser_fn)


def parser(parse_fn: ParseFunction[Input, Output]) -> Callable[[], Parser[Input, Output]]:
    """A decorator that creates a parser from the given function.

    Args:
        parse_fn (ParseFunction[Input, Output]): The parsing function to wrap.

    Returns:
        Callable[[], Parser[Input, Output]]: A function which returns the created parser.
    """

    @wraps(parse_fn)
    def wrapped() -> Parser[Input, Output]:
        return Parser(parse_fn)

    return wrapped


# TODO: Fix type hints and implementation of this.
def generate(
    parsers: Callable[
        [],
        Generator[Parser[Input, Output], ParseResult[Input, Output] | None, None],
    ],
) -> Parser[Input, Output]:
    @wraps(parsers)
    def parser_fn(inp: InputStream[Input]) -> ParseResult[Input, Output]:
        gen = parsers()
        value = None
        while True:
            try:
                parser = gen.send(value)
                result = parser.parse(inp)
                if isinstance(result, Error):
                    return result
                inp = result.input
                value = result
            except StopIteration as e:
                return e.value

    return Parser(parser_fn)
