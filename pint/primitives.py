from __future__ import annotations
from typing import Callable, TypeVar, Optional, Generic
from pint import Parser, ParseResult, ParseFunction, ParseError


def _symbol(expected: str) -> ParseFunction[None]:
    def parser(inp: str) -> ParseResult[None]:
        if inp[0 : len(expected)] == expected:
            return (expected[len(expected) :], None)
        else:
            return ParseError(inp, f"Expected to find {expected}")

    return parser


symbol = Parser(_symbol)
