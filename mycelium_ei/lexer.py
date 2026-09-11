"""Tokenizer for Mycelium-EI-Lang source text."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, List

from .errors import MyceliumSyntaxError


class TokenType(Enum):
    # Keywords
    ENVIRONMENT = "environment"
    FUNCTION = "function"
    MYCELIUM = "mycelium"
    NETWORK = "network"
    SIGNAL = "signal"
    ADAPT = "adapt"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    IN = "in"
    RETURN = "return"
    LET = "let"
    CONST = "const"
    NEW = "new"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"

    # Literals and names
    IDENTIFIER = "identifier"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"

    # Operators
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"
    EQUAL = "="
    EQUAL_EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    GREATER = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    AND = "&&"
    OR = "||"
    NOT = "!"
    ARROW = "->"

    # Punctuation
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    DOT = "."

    EOF = "end of file"


KEYWORDS = {
    "environment": TokenType.ENVIRONMENT,
    "function": TokenType.FUNCTION,
    "mycelium": TokenType.MYCELIUM,
    "network": TokenType.NETWORK,
    "signal": TokenType.SIGNAL,
    "adapt": TokenType.ADAPT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "return": TokenType.RETURN,
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "new": TokenType.NEW,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
}

TWO_CHAR = {
    "==": TokenType.EQUAL_EQUAL,
    "!=": TokenType.NOT_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    ">=": TokenType.GREATER_EQUAL,
    "&&": TokenType.AND,
    "||": TokenType.OR,
    "->": TokenType.ARROW,
}

ONE_CHAR = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "=": TokenType.EQUAL,
    "<": TokenType.LESS,
    ">": TokenType.GREATER,
    "!": TokenType.NOT,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "[": TokenType.LEFT_BRACKET,
    "]": TokenType.RIGHT_BRACKET,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ";": TokenType.SEMICOLON,
    ".": TokenType.DOT,
}

ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "0": "\0"}


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class Lexer:
    """Turns source text into a list of tokens ending with EOF."""

    def __init__(self, source: str, filename: str = "<string>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self, message: str) -> MyceliumSyntaxError:
        return MyceliumSyntaxError(message, self.line, self.column, self.filename)

    def tokenize(self) -> List[Token]:
        while True:
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    # -- helpers ---------------------------------------------------------

    def _peek(self, offset: int = 0) -> str:
        index = self.pos + offset
        if index < len(self.source):
            return self.source[index]
        return ""

    def _advance(self) -> str:
        char = self.source[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _add(self, token_type: TokenType, value: Any, line: int, column: int) -> None:
        self.tokens.append(Token(token_type, value, line, column))

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            char = self._peek()
            if char in " \t\r\n":
                self._advance()
            elif char == "/" and self._peek(1) == "/":
                while self.pos < len(self.source) and self._peek() != "\n":
                    self._advance()
            elif char == "/" and self._peek(1) == "*":
                start_line, start_col = self.line, self.column
                self._advance()
                self._advance()
                while self.pos < len(self.source) and not (self._peek() == "*" and self._peek(1) == "/"):
                    self._advance()
                if self.pos >= len(self.source):
                    raise MyceliumSyntaxError("Unterminated block comment", start_line, start_col, self.filename)
                self._advance()
                self._advance()
            else:
                break

    def _scan_token(self) -> None:
        line, column = self.line, self.column
        char = self._peek()

        if char.isdigit():
            self._scan_number(line, column)
            return
        if char.isalpha() or char == "_":
            self._scan_identifier(line, column)
            return
        if char == '"':
            self._scan_string(line, column)
            return

        two = self.source[self.pos:self.pos + 2]
        if two in TWO_CHAR:
            self._advance()
            self._advance()
            self._add(TWO_CHAR[two], two, line, column)
            return
        if char in ONE_CHAR:
            self._advance()
            self._add(ONE_CHAR[char], char, line, column)
            return
        if char in "&|":
            raise self.error(f"Unexpected character '{char}' (did you mean '{char}{char}'?)")
        raise self.error(f"Unexpected character {char!r}")

    def _scan_number(self, line: int, column: int) -> None:
        start = self.pos
        while self._peek().isdigit():
            self._advance()
        is_float = False
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()
        if self._peek() in ("e", "E") and (self._peek(1).isdigit() or
                                            (self._peek(1) in "+-" and self._peek(2).isdigit())):
            is_float = True
            self._advance()
            if self._peek() in "+-":
                self._advance()
            while self._peek().isdigit():
                self._advance()
        text = self.source[start:self.pos]
        if self._peek().isalpha() or self._peek() == "_":
            raise self.error(f"Invalid number literal '{text}{self._peek()}'")
        if is_float:
            self._add(TokenType.FLOAT, float(text), line, column)
        else:
            self._add(TokenType.INTEGER, int(text), line, column)

    def _scan_identifier(self, line: int, column: int) -> None:
        start = self.pos
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        text = self.source[start:self.pos]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        if token_type is TokenType.TRUE:
            self._add(token_type, True, line, column)
        elif token_type is TokenType.FALSE:
            self._add(token_type, False, line, column)
        elif token_type is TokenType.NULL:
            self._add(token_type, None, line, column)
        else:
            self._add(token_type, text, line, column)

    def _scan_string(self, line: int, column: int) -> None:
        self._advance()  # opening quote
        chars: List[str] = []
        while True:
            if self.pos >= len(self.source):
                raise MyceliumSyntaxError("Unterminated string", line, column, self.filename)
            char = self._advance()
            if char == '"':
                break
            if char == "\n":
                raise MyceliumSyntaxError("Unterminated string (newline inside quotes)", line, column,
                                          self.filename)
            if char == "\\":
                if self.pos >= len(self.source):
                    raise MyceliumSyntaxError("Unterminated string", line, column, self.filename)
                escaped = self._advance()
                if escaped not in ESCAPES:
                    raise self.error(f"Unknown escape sequence '\\{escaped}'")
                chars.append(ESCAPES[escaped])
            else:
                chars.append(char)
        self._add(TokenType.STRING, "".join(chars), line, column)


def tokenize(source: str, filename: str = "<string>") -> List[Token]:
    """Convenience wrapper: tokenize ``source`` and return the token list."""
    return Lexer(source, filename).tokenize()
