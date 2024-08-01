"""A user friendly parser combinator library for python."""

from __future__ import annotations

from typing import Callable, Generic, NamedTuple, TypeAlias, TypeVar

__version__ = "0.1.0"

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
