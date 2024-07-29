"""A user friendly parser combinator library for python."""

from __future__ import annotations

__version__ = "0.1.0"

from typing import Callable, Generic, NamedTuple, TypeAlias, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")
ParseResult: TypeAlias = "Result[Input, Output] | Error"


class Error:
    """The default error type. It only contains an error message."""

    def __init__(self, message: str) -> None:
        """Creates a new Error.

        Args:
            message (str): The error message.
        """
        self.message = message


class Result(NamedTuple, Generic[Input, Output]):
    """Holds the result of a parsing function.

    A Result is a tuple consisting of an input of type Input and an output of type
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
        parser_fn (Callable[[Input], Result[Input, Output]]): The wrapped parsing function.
    """

    def __init__(self, parser_fn: Callable[[Input], ParseResult[Input, Output]]) -> None:
        """Creates a new Parser with the given parser function.

        Args:
            parser_fn (Callable[[Input], Result[Input, Output]]): The parsing function to wrap.
        """
        self.parser_fn = parser_fn

    def parse(self, inp: Input) -> ParseResult[Input, Output]:
        """Parse the given input with the wrapped parser_fn.

        Args:
            inp (str): _description_

        Returns:
            ParseResult[Input, Output]: _description_
        """
        return self.parser_fn(inp)
