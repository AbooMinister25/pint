from __future__ import annotations

from typing import TypeVar

Output = TypeVar("Output")


class Unexpected(Exception):
    def __init__(self):
        pass


class Unclosed(Exception):
    def __init__(self, unclosed: str):
        self.unclosed = unclosed


class Custom(Exception):
    def __init__(self, message: str):
        self.message = message


class ParseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
