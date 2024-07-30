"""A user friendly parser combinator library for python."""

from __future__ import annotations

from functools import wraps

from typing_extensions import ParamSpec

__version__ = "0.1.0"

from typing import Callable, Generic, NamedTuple, TypeAlias, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")
ParseResult: TypeAlias = "Result[Input, Output] | Error"
ParseFunction: TypeAlias = Callable[[Input], "ParseResult[Input, Output]"]


class Error:
    """The default error type. It only contains an error message."""

    def __init__(self, message: str) -> None:
        """Creates a new Error.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __eq__(self, other: object) -> bool:
        """.

        Args:
            other (Error): _description_

        Returns:
            bool: _description_
        """
        if isinstance(other, Error):
            return self.message == other.message

        return object.__eq__(self, other)


class Result(NamedTuple, Generic[Input, Output]):
    """Holds the result of a parsing function.

    A `Result` is a tuple consisting of an input of type Input and an output of type
    Output.

    Attributes:
        input (Input): The remainder of the input after parsing.
        output (Output): The parsed output.
    """

    input: Input
    output: Output


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

    def parse(self, inp: Input) -> ParseResult[Input, Output]:
        """Parse the given input with the wrapped parser_fn.

        Args:
            inp (Input): The input to parse.

        Returns:
            ParseResult[Input, Output]: The parsed result.
        """
        return self.parser_fn(inp)


T = TypeVar("T")
P = ParamSpec("P")


def parser(parse_fn: ParseFunction[Input, Output]) -> Callable[[], Parser[Input, Output]]:
    """A decorator that creates a parser from the given function.

    Args:
        parse_fn (ParseFunction[Input, Output]): The parsing function to wrap.

    Returns:
        Parser[Input, Output]: The created parser.
    """

    @wraps(parse_fn)
    def wrapped() -> Parser[Input, Output]:
        return Parser(parse_fn)

    return wrapped
