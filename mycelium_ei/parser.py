"""Recursive-descent parser: tokens in, ``nodes.Program`` out."""

from __future__ import annotations

from typing import List, Optional, Tuple

from . import nodes as N
from .errors import MyceliumSyntaxError
from .lexer import KEYWORDS, Token, TokenType, tokenize

ASSIGNABLE = (N.Identifier, N.Index, N.Property)


def describe(token: Token) -> str:
    if token.type is TokenType.EOF:
        return "end of file"
    if token.type is TokenType.STRING:
        return f'"{token.value}"'
    if token.type in (TokenType.INTEGER, TokenType.FLOAT):
        return str(token.value)
    if token.type is TokenType.TRUE:
        return "true"
    if token.type is TokenType.FALSE:
        return "false"
    if token.type is TokenType.NULL:
        return "null"
    return f"'{token.value}'"


class Parser:
    def __init__(self, tokens: List[Token], filename: str = "<string>"):
        self.tokens = tokens
        self.filename = filename
        self.current = 0

    # -- token helpers ---------------------------------------------------

    def peek(self, offset: int = 0) -> Token:
        index = min(self.current + offset, len(self.tokens) - 1)
        return self.tokens[index]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def at_end(self) -> bool:
        return self.peek().type is TokenType.EOF

    def check(self, *types: TokenType) -> bool:
        return self.peek().type in types

    def advance(self) -> Token:
        if not self.at_end():
            self.current += 1
        return self.previous()

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def error(self, message: str, token: Optional[Token] = None) -> MyceliumSyntaxError:
        token = token or self.peek()
        return MyceliumSyntaxError(message, token.line, token.column, self.filename)

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise self.error(f"{message}, found {describe(self.peek())}")

    def skip_separators(self) -> None:
        while self.match(TokenType.SEMICOLON):
            pass

    # -- entry -----------------------------------------------------------

    def parse(self) -> N.Program:
        first = self.peek()
        body = []
        self.skip_separators()
        while not self.at_end():
            body.append(self.declaration())
            self.skip_separators()
        return N.Program(first.line, first.column, body)

    # -- declarations ----------------------------------------------------

    def declaration(self):
        if self.check(TokenType.ENVIRONMENT):
            return self.environment_decl()
        if self.check(TokenType.FUNCTION) or (self.check(TokenType.ADAPT) and self.peek(1).type is TokenType.FUNCTION):
            return self.function_decl()
        if self.check(TokenType.MYCELIUM):
            return self.mycelium_decl()
        if self.check(TokenType.NETWORK) and self.peek(1).type is TokenType.IDENTIFIER:
            return self.network_decl()
        if self.check(TokenType.SIGNAL) and self.peek(1).type is TokenType.IDENTIFIER:
            return self.signal_decl()
        return self.statement()

    def environment_decl(self) -> N.EnvironmentDecl:
        start = self.advance()
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after 'environment'")
        entries = self.object_entries("environment block")
        return N.EnvironmentDecl(start.line, start.column, entries)

    def type_name(self) -> str:
        token = self.consume(TokenType.IDENTIFIER, "Expected a type name")
        name = token.value
        if self.check(TokenType.LEFT_BRACKET) and self.peek(1).type is TokenType.RIGHT_BRACKET:
            self.advance()
            self.advance()
            name += "[]"
        return name

    def function_decl(self) -> N.FunctionDecl:
        adapt = self.match(TokenType.ADAPT)
        start = self.consume(TokenType.FUNCTION, "Expected 'function'")
        name = self.consume(TokenType.IDENTIFIER, "Expected function name after 'function'").value
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after function name '{name}'")
        parameters: List[N.Parameter] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                pname = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
                ptype = self.type_name() if self.match(TokenType.COLON) else None
                parameters.append(N.Parameter(pname, ptype))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        return_type = self.type_name() if self.match(TokenType.ARROW) else None
        body = self.block(f"function '{name}'")
        return N.FunctionDecl(start.line, start.column, name, parameters, return_type, body, adapt)

    def network_decl(self) -> N.NetworkDecl:
        start = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected network name").value
        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' after network name '{name}'")
        entries = self.object_entries(f"network '{name}'")
        return N.NetworkDecl(start.line, start.column, name, entries)

    def signal_decl(self) -> N.SignalDecl:
        start = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected signal name").value
        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' after signal name '{name}'")
        fields: List[Tuple[str, str]] = []
        while not self.check(TokenType.RIGHT_BRACE):
            if self.at_end():
                raise self.error(f"Unterminated signal '{name}' (missing '}}')")
            fname = self.consume(TokenType.IDENTIFIER, "Expected field name in signal").value
            self.consume(TokenType.COLON, f"Expected ':' after field name '{fname}'")
            ftype = self.type_name()
            fields.append((fname, ftype))
            if not self.match(TokenType.COMMA, TokenType.SEMICOLON) and not self.check(TokenType.RIGHT_BRACE):
                if self.peek().line == self.previous().line:
                    raise self.error(f"Expected ',' or '}}' after field '{fname}', found {describe(self.peek())}")
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return N.SignalDecl(start.line, start.column, name, fields)

    def mycelium_decl(self) -> N.MyceliumDecl:
        start = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected mycelium name").value
        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' after mycelium name '{name}'")
        decl = N.MyceliumDecl(start.line, start.column, name)
        self.skip_separators()
        while not self.check(TokenType.RIGHT_BRACE):
            if self.at_end():
                raise self.error(f"Unterminated mycelium '{name}' (missing '}}')")
            if self.check(TokenType.SIGNAL):
                decl.fields.append(self.signal_field())
            elif self.check(TokenType.NETWORK):
                decl.fields.append(self.network_field())
            elif self.check(TokenType.FUNCTION) or (self.check(TokenType.ADAPT) and self.peek(1).type is TokenType.FUNCTION):
                decl.methods.append(self.function_decl())
            else:
                raise self.error(
                    f"Expected 'signal', 'network' or 'function' inside mycelium '{name}', found {describe(self.peek())}")
            self.match(TokenType.COMMA)
            self.skip_separators()
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return decl

    def signal_field(self) -> N.FieldDecl:
        start = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected signal field name").value
        type_name = self.type_name() if self.match(TokenType.COLON) else None
        default = self.expression() if self.match(TokenType.EQUAL) else None
        if type_name is None and default is None:
            raise self.error(f"Signal field '{name}' needs a type or a default value")
        return N.FieldDecl(start.line, start.column, name, type_name, default)

    def network_field(self) -> N.FieldDecl:
        start = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected network field name").value
        if self.match(TokenType.COLON):
            type_name = self.type_name()
            return N.FieldDecl(start.line, start.column, name, type_name, None)
        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' or ':' after network field '{name}'")
        entries = self.object_entries(f"network '{name}'")
        return N.FieldDecl(start.line, start.column, name, None, None, entries)

    def object_entries(self, what: str) -> List[Tuple[str, N.Expr]]:
        """Parse ``key: value`` pairs up to and including the closing brace."""
        entries: List[Tuple[str, N.Expr]] = []
        while not self.check(TokenType.RIGHT_BRACE):
            if self.at_end():
                raise self.error(f"Unterminated {what} (missing '}}')")
            key_token = self.peek()
            if key_token.type in (TokenType.IDENTIFIER, TokenType.STRING):
                self.advance()
                key = key_token.value
            elif key_token.value is not None and key_token.type in KEY_LIKE_KEYWORDS:
                self.advance()
                key = str(key_token.value)
            else:
                raise self.error(f"Expected a key in {what}, found {describe(key_token)}")
            self.consume(TokenType.COLON, f"Expected ':' after key '{key}'")
            value = self.expression()
            entries.append((key, value))
            if not self.match(TokenType.COMMA) and not self.check(TokenType.RIGHT_BRACE):
                if self.peek().line == self.previous().line:
                    raise self.error(f"Expected ',' or '}}' after value for '{key}', found {describe(self.peek())}")
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return entries

    # -- statements ------------------------------------------------------

    def block(self, what: str) -> N.Block:
        start = self.consume(TokenType.LEFT_BRACE, f"Expected '{{' to start {what}")
        statements = []
        self.skip_separators()
        while not self.check(TokenType.RIGHT_BRACE):
            if self.at_end():
                raise self.error(f"Unterminated {what} (missing '}}')", start)
            statements.append(self.statement())
            self.skip_separators()
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return N.Block(start.line, start.column, statements)

    def statement(self):
        if self.check(TokenType.LET, TokenType.CONST):
            return self.let_statement()
        if self.check(TokenType.IF):
            return self.if_statement()
        if self.check(TokenType.WHILE):
            return self.while_statement()
        if self.check(TokenType.FOR):
            return self.for_statement()
        if self.check(TokenType.RETURN):
            return self.return_statement()
        if self.check(TokenType.FUNCTION, TokenType.MYCELIUM, TokenType.ENVIRONMENT):
            raise self.error(f"{describe(self.peek())} declarations are only allowed at the top level")
        if self.check(TokenType.ELSE):
            raise self.error("'else' without a matching 'if'")
        start = self.peek()
        expression = self.expression()
        return N.ExpressionStatement(start.line, start.column, expression)

    def let_statement(self) -> N.Let:
        start = self.advance()
        constant = start.type is TokenType.CONST
        name = self.consume(TokenType.IDENTIFIER, f"Expected variable name after '{start.value}'").value
        type_name = self.type_name() if self.match(TokenType.COLON) else None
        self.consume(TokenType.EQUAL, f"Expected '=' after variable name '{name}'")
        value = self.expression()
        return N.Let(start.line, start.column, name, type_name, value, constant)

    def if_statement(self) -> N.If:
        start = self.advance()
        condition = self.expression()
        then_branch = self.block("if body")
        else_branch = None
        if self.match(TokenType.ELSE):
            if self.check(TokenType.IF):
                else_branch = self.if_statement()
            else:
                else_branch = self.block("else body")
        return N.If(start.line, start.column, condition, then_branch, else_branch)

    def while_statement(self) -> N.While:
        start = self.advance()
        condition = self.expression()
        body = self.block("while body")
        return N.While(start.line, start.column, condition, body)

    def for_statement(self) -> N.For:
        start = self.advance()
        variable = self.consume(TokenType.IDENTIFIER, "Expected loop variable after 'for'").value
        self.consume(TokenType.IN, f"Expected 'in' after loop variable '{variable}'")
        iterable = self.expression()
        body = self.block("for body")
        return N.For(start.line, start.column, variable, iterable, body)

    def return_statement(self) -> N.Return:
        start = self.advance()
        value = None
        nxt = self.peek()
        if not self.check(TokenType.RIGHT_BRACE, TokenType.SEMICOLON, TokenType.EOF) and nxt.line == start.line:
            value = self.expression()
        return N.Return(start.line, start.column, value)

    # -- expressions -----------------------------------------------------

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logical_or()
        if self.check(TokenType.EQUAL):
            equals = self.advance()
            value = self.assignment()
            if not isinstance(expr, ASSIGNABLE):
                raise self.error("Invalid assignment target (expected a variable, index or property)", equals)
            return N.Assign(expr.line, expr.column, expr, value)
        return expr

    def logical_or(self):
        expr = self.logical_and()
        while self.match(TokenType.OR):
            right = self.logical_and()
            expr = N.Logical(expr.line, expr.column, expr, "||", right)
        return expr

    def logical_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            right = self.equality()
            expr = N.Logical(expr.line, expr.column, expr, "&&", right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous().value
            right = self.comparison()
            expr = N.Binary(expr.line, expr.column, expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            operator = self.previous().value
            right = self.term()
            expr = N.Binary(expr.line, expr.column, expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().value
            right = self.factor()
            expr = N.Binary(expr.line, expr.column, expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self.previous().value
            right = self.unary()
            expr = N.Binary(expr.line, expr.column, expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous()
            operand = self.unary()
            return N.Unary(operator.line, operator.column, operator.value, operand)
        return self.postfix()

    def postfix(self):
        expr = self.primary()
        while True:
            token = self.peek()
            same_line = token.line == self.previous().line
            if token.type is TokenType.LEFT_PAREN and same_line:
                self.advance()
                arguments = self.arguments()
                expr = N.Call(expr.line, expr.column, expr, arguments)
            elif token.type is TokenType.LEFT_BRACKET and same_line:
                self.advance()
                index = self.expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after index")
                expr = N.Index(expr.line, expr.column, expr, index)
            elif token.type is TokenType.DOT:
                self.advance()
                name = self.property_name()
                expr = N.Property(expr.line, expr.column, expr, name)
            else:
                return expr

    def property_name(self) -> str:
        """A property name after '.'; keywords are allowed here (``stats.environment``)."""
        token = self.peek()
        if token.type is TokenType.IDENTIFIER or (token.type in KEYWORD_TYPES and isinstance(token.value, str)):
            self.advance()
            return token.value
        raise self.error(f"Expected property name after '.', found {describe(token)}")

    def arguments(self) -> List[N.Expr]:
        arguments: List[N.Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        return arguments

    def primary(self):
        token = self.peek()
        t = token.type
        if t in (TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, TokenType.TRUE, TokenType.FALSE, TokenType.NULL):
            self.advance()
            return N.Literal(token.line, token.column, token.value)
        if t is TokenType.IDENTIFIER:
            self.advance()
            return N.Identifier(token.line, token.column, token.value)
        if t is TokenType.LEFT_PAREN:
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        if t is TokenType.LEFT_BRACKET:
            self.advance()
            elements: List[N.Expr] = []
            while not self.check(TokenType.RIGHT_BRACKET):
                if self.at_end():
                    raise self.error("Unterminated array literal (missing ']')", token)
                elements.append(self.expression())
                if not self.match(TokenType.COMMA) and not self.check(TokenType.RIGHT_BRACKET):
                    raise self.error(f"Expected ',' or ']' in array literal, found {describe(self.peek())}")
            self.advance()
            return N.ArrayLiteral(token.line, token.column, elements)
        if t is TokenType.LEFT_BRACE:
            self.advance()
            entries = self.object_entries("object literal")
            return N.ObjectLiteral(token.line, token.column, entries)
        if t is TokenType.NEW:
            self.advance()
            name = self.consume(TokenType.IDENTIFIER, "Expected a mycelium name after 'new'").value
            arguments: List[N.Expr] = []
            if self.match(TokenType.LEFT_PAREN):
                arguments = self.arguments()
            return N.New(token.line, token.column, name, arguments)
        if t is TokenType.EOF:
            raise self.error("Unexpected end of file")
        raise self.error(f"Unexpected token {describe(token)}")


KEYWORD_TYPES = {token_type for token_type in KEYWORDS.values()}
KEY_LIKE_KEYWORDS = KEYWORD_TYPES - {TokenType.TRUE, TokenType.FALSE, TokenType.NULL}


def parse(source: str, filename: str = "<string>") -> N.Program:
    """Tokenize and parse ``source`` into a ``Program``."""
    return Parser(tokenize(source, filename), filename).parse()
