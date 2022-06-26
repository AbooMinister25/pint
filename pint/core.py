from __future__ import annotations
from typing import Callable, TypeVar, Optional


class ParseError(Exception):
    def __init__(
        self,
        input: ParseFunction[T],
        parser: Parser,
        message: Optional[str] = "Error occurred while parsing",
    ):
        super().__init__(message)


T = TypeVar("T")
ParseResult = tuple[str, T] | ParseError

ParseFunction = Callable[[str], ParseResult[T]]


class Parser:
    def __init__(self, parser: ParseFunction[T]):
        self.parser = parser
        self.description = None
