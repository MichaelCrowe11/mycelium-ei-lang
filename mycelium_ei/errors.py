"""Error types raised by the Mycelium-EI-Lang lexer, parser and interpreter."""

from __future__ import annotations

from typing import Optional


class MyceliumError(Exception):
    """Base class for every error a Mycelium program can raise.

    ``line`` and ``column`` are 1-based positions in the source file when known.
    """

    kind = "error"

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None,
                 filename: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename

    def __str__(self) -> str:
        return self.message

    def format(self) -> str:
        """Render as ``file:line:col: kind: message`` (parts omitted when unknown)."""
        where = []
        if self.filename:
            where.append(self.filename)
        if self.line is not None:
            where.append(str(self.line))
            if self.column is not None:
                where.append(str(self.column))
        prefix = ":".join(where)
        if prefix:
            return f"{prefix}: {self.kind}: {self.message}"
        return f"{self.kind}: {self.message}"


class MyceliumSyntaxError(MyceliumError):
    """Raised by the lexer or parser."""

    kind = "syntax error"


class MyceliumRuntimeError(MyceliumError):
    """Raised while a program runs."""

    kind = "runtime error"
