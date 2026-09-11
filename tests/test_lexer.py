import pytest

from mycelium_ei.errors import MyceliumSyntaxError
from mycelium_ei.lexer import TokenType, tokenize


def types(source):
    return [t.type for t in tokenize(source)]


def test_let_with_type_annotation_and_comment():
    assert types("let x: float = 1.5 // comment") == [
        TokenType.LET, TokenType.IDENTIFIER, TokenType.COLON, TokenType.IDENTIFIER,
        TokenType.EQUAL, TokenType.FLOAT, TokenType.EOF,
    ]


def test_two_character_operators():
    assert types("a && b || !c != d <= e >= f == g -> h") == [
        TokenType.IDENTIFIER, TokenType.AND, TokenType.IDENTIFIER, TokenType.OR, TokenType.NOT,
        TokenType.IDENTIFIER, TokenType.NOT_EQUAL, TokenType.IDENTIFIER, TokenType.LESS_EQUAL,
        TokenType.IDENTIFIER, TokenType.GREATER_EQUAL, TokenType.IDENTIFIER, TokenType.EQUAL_EQUAL,
        TokenType.IDENTIFIER, TokenType.ARROW, TokenType.IDENTIFIER, TokenType.EOF,
    ]


def test_keywords_and_literals():
    tokens = tokenize('environment mycelium network signal adapt new true false null "hi"')
    assert [t.type for t in tokens[:9]] == [
        TokenType.ENVIRONMENT, TokenType.MYCELIUM, TokenType.NETWORK, TokenType.SIGNAL,
        TokenType.ADAPT, TokenType.NEW, TokenType.TRUE, TokenType.FALSE, TokenType.NULL,
    ]
    assert tokens[6].value is True
    assert tokens[7].value is False
    assert tokens[8].value is None
    assert tokens[9].type is TokenType.STRING and tokens[9].value == "hi"


def test_numbers():
    tokens = tokenize("10 1.5 1.5e3 2E-2 7.")
    assert [(t.type, t.value) for t in tokens[:-1]] == [
        (TokenType.INTEGER, 10), (TokenType.FLOAT, 1.5), (TokenType.FLOAT, 1500.0),
        (TokenType.FLOAT, 0.02), (TokenType.INTEGER, 7), (TokenType.DOT, "."),
    ]


def test_string_escapes():
    (token, _eof) = tokenize(r'"a\"b\n\t\\"')
    assert token.value == 'a"b\n\t\\'


def test_line_and_column_tracking():
    tokens = tokenize("let a = 1\n\n  let b = 2")
    b_let = tokens[4]
    assert (b_let.type, b_let.line, b_let.column) == (TokenType.LET, 3, 3)


def test_block_comments_are_skipped():
    assert types("1 /* a\n multi line */ + /* x */ 2") == [TokenType.INTEGER, TokenType.PLUS, TokenType.INTEGER, TokenType.EOF]


@pytest.mark.parametrize("source, message", [
    ('"open', "Unterminated string"),
    ('"line\nbreak"', "newline inside quotes"),
    ("/* never closed", "Unterminated block comment"),
    ("a & b", "did you mean '&&'"),
    ("a | b", "did you mean '||'"),
    ("x = 5abc", "Invalid number literal"),
    ("let y = @", "Unexpected character '@'"),
    (r'"bad \q escape"', "Unknown escape sequence"),
])
def test_lexer_errors(source, message):
    with pytest.raises(MyceliumSyntaxError) as info:
        tokenize(source)
    assert message in str(info.value)
    assert info.value.line >= 1


def test_error_reports_position_and_filename():
    with pytest.raises(MyceliumSyntaxError) as info:
        tokenize("let a = 1\nlet b = $", filename="prog.myc")
    err = info.value
    assert (err.line, err.column, err.filename) == (2, 9, "prog.myc")
    assert err.format() == "prog.myc:2:9: syntax error: Unexpected character '$'"
