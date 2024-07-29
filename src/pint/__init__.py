"""A user friendly parser combinator library for python."""

from __future__ import annotations

__version__ = "0.1.0"

from typing import Generic, NamedTuple, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")


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
