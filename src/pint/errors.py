from __future__ import annotations

from typing import TypeVar

Output = TypeVar("Output")


class UnexpectedError(Exception):
    """Raised when an unexpected input is found."""

    def __init__(self) -> None:
        """Creates an unexpected error."""


class UnclosedError(Exception):
    """Raised when an unclosed delimiter occurs."""

    def __init__(self, unclosed: str) -> None:
        """Creates an unclosed error with the given unclosed delimiter.

        Args:
            unclosed (str): The unclosed delimiter.
        """
        self.unclosed = unclosed


class CustomError(Exception):
    """Custom error with a message."""

    def __init__(self, message: str) -> None:
        """Creates a custom error with the given message.

        Args:
            message (str): The error message.
        """
        self.message = message


class ParseError(Exception):
    """General parse error with a message."""

    def __init__(self, message: str) -> None:
        """Creates a parse error with the given message.

        Args:
            message (str): The error message.
        """
        self.message = message
        super().__init__(message)
