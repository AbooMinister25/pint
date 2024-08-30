from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")
Input = TypeVar("Input")


@dataclass
class Span:
    """Represents the span of some item in the input to a parser."""

    start: int
    end: int

    def __str__(self) -> str:
        """The string representation of this span."""
        return f"{self.start}:{self.end}"

    def __contains__(self, other: object) -> bool:
        """The contains implementation of a span.

        If `other` is a `Span`, this will return True if:
        `self.start <= other.start and self.end >= other.end`
        """
        if isinstance(other, Span):
            return self.start <= other.start and self.end >= other.end

        return False


class Error:
    """The default error type."""

    def __init__(self, span: Span, label: Optional[str] = None) -> None:
        """Creates a new Error.

        Args:
            span (Span): The location in the input where this error occurred.
            label (Optional[str]): An optional label which represents which parser
            this error happened under. Defaults to None.
        """
        self.span = span
        self.label = label

    def __str__(self) -> str:
        """The string representation of this error."""
        return f"Error: Error in parser {self.label if self.label else ""} at {self.span}."


class ExpectedError(Error, Generic[T]):
    """Error that's created when a parser expected to find one of the given items,
    but found something else instead.
    """

    def __init__(
        self,
        expected: list[T],
        found: T,
        span: Span,
        label: Optional[str] = None,
    ) -> None:
        """Creates a new ExpectedError.

        Args:
            expected (list[T]): A list of items that were expected.
            found (T): The item which was found.
            span (Span): The location in the input where this error occurred.
            label (Optional[str]): An optional label which represents which parser
            this error happened under. Defaults to None.
        """
        self.expected = expected
        self.found = found
        super().__init__(span, label)

    def __str__(self) -> str:
        """The string representation of this error."""
        return f"Expected {self.expected}, instead found {self.found}"


class UnclosedError(Error, Generic[T]):
    """Error that's created when a parser encounters an unclosed delimiter."""

    def __init__(self, delimiter: T, span: Span, label: Optional[str] = None) -> None:
        """Creates a new UnclosedError.

        Args:
            delimiter (T): The unclosed delimiter.
            span (Span): The location in the input where this error occurred.
            label (Optional[str]): An optional label which represents which parser
            this error happened under. Defaults to None.
        """
        self.delimiter = delimiter
        super().__init__(span, label)

    def __str__(self) -> str:
        """The string representation of this error."""
        return f"Unclosed delimiter {self.delimiter}"


class UnexpectedError(Error, Generic[T]):
    """Error that's created when a parser encounters an unexpected item."""

    def __init__(self, found: T, span: Span, label: Optional[str] = None) -> None:
        """Creates a new UnexpectedError.

        Args:
            found (T): The item which was found.
            span (Span): The location in the input where this error occurred.
            label (Optional[str]): An optional label which represents which parser
            this error happened under. Defaults to None.
        """
        self.found = found
        super().__init__(span, label)

    def __str__(self) -> str:
        """The string representation of this error."""
        return f"Unexpected item {self.found}"


class CustomError(Error):
    """An error that's created with a custom error message.."""

    def __init__(self, message: str, span: Span, label: Optional[str] = None) -> None:
        """Creates a new CustomError.

        Args:
            message (str): The error message.
            span (Span): The location in the input where this error occurred.
            label (Optional[str]): An optional label which represents which parser
            this error happened under. Defaults to None.
        """
        self.message = message
        super().__init__(span, label)

    def __str__(self) -> str:
        """The string representation of this error."""
        return self.message


def make_report(inp: str, error: Error) -> str:
    """Creates a formatted error report for the given error.

    This will only work when the input provided is a string.

    Args:
        inp (str): The input given to the parsers.
        error (Error): The error to make a report of.

    Returns:
        str: The formatted error report.
    """
    lines = extract_lines(inp)
    lineno = 0
    error_line = (inp, error.span)
    for line, span in lines:
        if error.span in span:
            lineno = lines.index((line, span)) + 1
            error_line: tuple[str, Span] = line, span

    indent_amount = error.span.start - error_line[1].start

    message = f"Error at line {lineno}"
    if error.label:
        message += f", in parser {error.label}"
    message += f":\n    {error_line[0]}\n    "
    message += " " * indent_amount + "^\n"
    message += str(error)
    return message


def extract_lines(inp: str) -> list[tuple[str, Span]]:
    ret: list[tuple[str, Span]] = []
    start = 0

    for line in inp.splitlines():
        ret.append((line, Span(start, start + len(line))))
        start += len(line) + 1  # to account for the newline.

    return ret
