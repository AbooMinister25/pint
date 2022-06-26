from __future__ import annotations
from typing import Callable, TypeVar, Optional, Generic


class ParseError(Exception):
    """Represents an error that occurred during parsing,

    Args:
        input (str): The input being parsed.
        message (Optional[str]): The error message to use.
    """

    def __init__(
        self,
        input: str,
        message: Optional[str] = "Error occurred while parsing",
    ):
        super().__init__(message)


T = TypeVar("T")
ParseResult = tuple[str, T] | ParseError

ParseFunction = Callable[[str], ParseResult[T]]
ParseBuilder = Callable[..., ParseFunction[T]]

Output = TypeVar("Output")


class Parser(Generic[Output]):
    """Wraps a parser and implements combinators for that parser

    Args:
        parser (ParseFunction[T]): The parsing function.

    Attributes:
        parser (ParseFunction[T]): The function being wrapped.
        label (Optional[str]): The label for the parser, used for more descriptive error messages.
    """

    def __init__(self, parser: ParseBuilder[Output]):
        self.parser = parser
        self.label: Optional[str] = None

    def parse(self, input: str) -> ParseResult[Output]:
        return self.parser(input)
