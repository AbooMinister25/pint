from __future__ import annotations
from typing import Callable, TypeVar, Optional, Generic, Any
from pint.core import ParseResult, ParseFunction, ParseError

Output = TypeVar("Output")
MappedOutput = TypeVar("MappedOutput")
ThenOutput = TypeVar("ThenOutput")


class Parser(Generic[Output]):
    """Wraps a parser and implements combinators

    Args:
        parser (ParseFunction[T]): The parsing function.

    Attributes:
        parser (ParseFunction[T]): The function being wrapped.
        label (Optional[str]): The label for the parser, used for more descriptive error messages.
    """

    def __init__(self, parser: ParseFunction[Output]):
        self.parser = parser
        self.label: Optional[str] = None

    def parse(self, inp: str) -> ParseResult[Output]:
        """Parse the given input and return a `ParseResult`

        Args:
            input (str): The input to parse.

        Returns:
            ParseResult[Output]: Either a tuple consisting of the remaining input after parsing,
            and the type of `Output`, or a `ParseError`.
        """
        return self.parser(inp)

    def map_to(
        self, function: Callable[[Output], MappedOutput]
    ) -> Parser[MappedOutput]:
        """Combinator which maps the output of this parser to the output
        type of `function`.

        Args:
            function (Callable[[Output], MappedOutput]): The function to apply
            on the output of this parser.

        Returns:
            Parser[MappedOutput]: A parser which outputs `MappedOutput`, the
            output type of `function`.

        Examples:
            >>> from pint import ident
            >>> last_letter = ident().map_to(lambda x: x[-1])
            >>> print(last_letter.parse("hello"))
        """

        def parser(inp: str) -> ParseResult[MappedOutput]:
            res = self.parse(inp)
            if isinstance(res, ParseError):
                return res

            return (res[0], function(res[1]))

        return Parser(parser)

    def then(self, then_p: Parser[ThenOutput]) -> Parser[tuple[Output, ThenOutput]]:
        """Combinator which chains this parser with another one, returning
        a parser which successively returns their results.

        Args:
            then_p (Parser[ThenOutput]): The parser to chain with this one.

        Returns:
            Parser[tuple[Output, ThenOutput]]: A parser which returns a tuple
            of the result of this parer and the next one.
        """

        def parser(inp: str) -> ParseResult[tuple[Output, ThenOutput]]:
            res_1 = self.parse(inp)
            if isinstance(res_1, ParseError):
                return res_1

            remaining_input, result = res_1
            res_2 = then_p.parse(remaining_input)
            if isinstance(res_2, ParseError):
                return res_2

            return (res_2[0], (result, res_2[1]))

        return Parser(parser)

    def then_ignore(self, then_p: Parser[Any]) -> Parser[Output]:
        def parser(inp: str) -> ParseResult[Output]:
            p = self.then(then_p)

            res = p.parse(inp)
            if isinstance(res, ParseError):
                return res

            return (res[0], res[1][0])

        return Parser(parser)

    def ignore_then(self, then_p: Parser[Any]) -> Parser[Output]:
        def parser(inp: str) -> ParseResult[Output]:
            p = self.then(then_p)

            res = p.parse(inp)
            if isinstance(res, ParseError):
                return res

            return (res[0], res[1][1])

        return Parser(parser)

    def padded_whitespace(self) -> Parser[None]:
        def parser(inp: str) -> ParseResult[None]:
            return (
                take_or_not(" ")
                .ignore_then(self)
                .then_ignore(take_or_not(" "))
                .parse(inp)
            )

        return Parser(parser)

    def with_label(self, label: str) -> Parser[Output]:
        """Assigns a label to this parser. Can allow for more
        descriptive error messages.

        Args:
            label (str): The label to use.

        Returns:
            Parser[Output]: A parser which outputs `Output`, which
            is the same output of this parser.
        """
        self.label = label
        return self


def symbol(expected: str) -> Parser[str]:
    """Parser which only accepts the given item.

    Args:
        expected (str): The expected string.

    Returns:
        Parser[None]: A parser which outputs `str`.

    Examples:
        >>> from pint import symbol
        >>> parse_a = symbol("a")
        >>> print(parse_a.parse("a"))
        >>> print(parse_a.parse("b"))
    """

    def parser(inp: str) -> ParseResult[str]:
        if inp[0 : len(expected)] == expected:
            return (inp[len(expected) :], inp[0 : len(expected)])
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
            return ParseError(inp, "Expected an identifier")

        for char in inp:
            if char.isidentifier():
                ident += char
            else:
                break

        return (inp[len(ident) :], ident)

    return Parser(parser)


def take_while(function: Callable[[str], bool]) -> Parser[str]:
    """Parser which parses input as long as the input fulfills
    the given condition.

    Args:
        function (Callable[[str], bool]): The function to be used
        on the values of the input to check whether they pass a condition.

    Returns:
        Parser[str]: A parser which outputs `str`.

    Examples:
        >>> from pint import take_while
        >>> number_parser = take_while(lambda c: c.isnumeric())
        >>> print(number_parser.parse("10"))
    """

    def parser(inp: str) -> ParseResult[str]:
        ret = ""

        if not function(inp[0]):
            return ParseError(inp, "Invalid input")

        for char in inp:
            if function(char):
                ret += char
            else:
                break

        return (inp[len(ret) :], ret)

    return Parser(parser)


def take_or_not(char: str) -> Parser[None]:
    """Parser which takes a given character if it is found,
    and if not, returns the given input

    Args:
        char (str): The character to check for.

    Returns:
        Parser[None]: A parser which outputs `None`.
    """

    def parser(inp: str) -> ParseResult[None]:
        if inp[0] == char:
            return (inp[1:], None)

        return (inp, None)

    return Parser(parser)
