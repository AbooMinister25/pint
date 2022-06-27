from __future__ import annotations
from typing import Callable, TypeVar, Optional


class ParseError:
    """Represents an error that occurred during parsing,

    Args:
        input (str): The input being parsed.
        message (Optional[str]): The error message to use.
    """

    def __init__(
        self,
        inp: str,
        message: str = "Error occurred while parsing",
    ):
        self.message = message


T = TypeVar("T")
ParseResult = tuple[str, T] | ParseError
ParseFunction = Callable[[str], ParseResult[T]]
