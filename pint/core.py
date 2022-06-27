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

Output = TypeVar("Output")
MappedOutput = TypeVar("MappedOutput")


class Parser(Generic[Output]):
    """Wraps a parser and implements combinators

    Args:
        parser (ParseFunction[T]): The parsing function.

    Attributes:
        parser (ParseFunction[T]): The function being wrapped.
        label (Optional[str]): The label for the parser, used for more descriptive error messages.
    """

    def __init__(self, parser: ParseFunction[Output]):
        self.parser = parser
        self.label: Optional[str] = None

    def parse(self, input: str) -> ParseResult[Output]:
        """Parse the given input and return a `ParseResult`

        Args:
            input (str): The input to parse.

        Returns:
            ParseResult[Output]: Either a tuple consisting of the remaining input after parsing,
            and the type of `Output`, or a `ParseError`.
        """
        return self.parser(input)

    def map(self, function: Callable[[Output], MappedOutput]) -> Parser[MappedOutput]:
        """Combinator which maps the output of this parser to the output
        type of `function`.

        Args:
            function (Callable[[Output], MappedOutput]): The function to apply
            on the output of this parser.

        Returns:
            Parser[MappedOutput]: A parser which outputs `MappedOutput`, the
            output type of `function`.
        """

        def parser(input: str) -> ParseResult[MappedOutput]:
            res = self.parse(input)
            if isinstance(res, ParseError):
                return res

            return (res[0], function(res[1]))

        return Parser(parser)
