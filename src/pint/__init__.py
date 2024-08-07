"""A user friendly parser combinator library for python."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generic, NamedTuple, TypeAlias, TypeVar

if TYPE_CHECKING:
    from collections.abc import Sequence

__version__ = "0.1.0"

T = TypeVar("T")
Input = TypeVar("Input")
Output = TypeVar("Output", covariant=True)
ParseResult: TypeAlias = "Result[InputStream[Input], Output] | Error"
ParseFunction: TypeAlias = Callable[["InputStream[Input]"], "ParseResult[Input, Output]"]


class Error:
    """The default error type. It only contains an error message."""

    def __init__(self, message: str) -> None:
        """Creates a new Error.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __eq__(self, other: object) -> bool:
        """If other is an Error, compare messages for equality.

        Args:
            other (Error): _description_

        Returns:
            bool: _description_
        """
        if isinstance(other, Error):
            return self.message == other.message

        return object.__eq__(self, other)

    def __str__(self) -> str:
        """Return error message.

        Returns:
            str: The error message.
        """
        return self.message

    def __repr__(self) -> str:
        """Return error message.

        Returns:
            str: The error message.
        """
        return f"Error {self.__class__} with message: {self.message}"


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


@dataclass(frozen=True)
class InputStream(Generic[T]):
    """The input stream that a parser works with.

    This wraps a `Sequence[T]` and uses the `position` attribute to keep
    track of where a parser is in the input in parsing. This is mainly useful
    for error reporting.

    Attributes:
        stream (Sequence[T]): The stream that this InputStream wraps.
        position (int): The position in the input string. Defaults to 0.
    """

    stream: Sequence[T]
    position: int = 0

    def take(self, amount: int) -> tuple[Sequence[T], InputStream[T]]:
        """Takes the given `amount` from the stream which this input wraps and
        returns the taken content and a new `InputStream` with the remaining content.

        Args:
            amount (int): The amount to take.

        Returns:
            tuple[Sequence[T], InputStream[T]]: A tuple of the content that was taken,
            and an `InputStream` with the remaining content.

        Raises:
            IndexError: If the given `amount` is larger than the length of the stream.
        """
        if amount > len(self.stream):
            raise IndexError("Amount out of range.")

        taken = self.stream[:amount]
        position = self.position + len(taken)
        return (taken, InputStream(self.stream[amount:], position))

    def index(self, pattern: T) -> int:
        """Returns the lowest index in the stream where `pattern` is found.

        Args:
            pattern (T): The pattern to search for.

        Returns:
            int: The index at which it is found.

        Raises:
            ValueError: When the substring is not found.
        """
        return self.stream.index(pattern)

    def __eq__(self, other: object) -> bool:
        """Compare this `InputStream` with another object."""
        if isinstance(other, InputStream):
            return self.stream == other.stream and self.position == other.position  # type: ignore  # noqa: PGH003

        return self.stream == other
