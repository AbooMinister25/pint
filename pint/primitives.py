from __future__ import annotations
from typing import Callable, TypeVar, Optional, Generic
from pint import Parser, ParseResult, ParseFunction, ParseError


def symbol(expected: str) -> Parser[None]:
    def parser(inp: str) -> ParseResult[None]:
        if inp[0 : len(expected)] == expected:
            return (expected[len(expected) :], None)
        else:
            return ParseError(inp, f"Expected to find {expected}")

    return Parser(parser)
