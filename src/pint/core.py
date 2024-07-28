from __future__ import annotations

from typing import Callable, TypeVar

T = TypeVar("T")
ParseResult = tuple[str, T]
ParseFunction = Callable[[str], ParseResult[T]]
