import pytest

from mycelium_ei import nodes as N
from mycelium_ei.errors import MyceliumSyntaxError
from mycelium_ei.parser import parse


def expr(source):
    program = parse(source)
    assert len(program.body) == 1
    return program.body[0].expression


def test_precedence_multiplication_before_addition():
    node = expr("1 + 2 * 3")
    assert isinstance(node, N.Binary) and node.operator == "+"
    assert isinstance(node.right, N.Binary) and node.right.operator == "*"


def test_comparison_and_logic_precedence():
    node = expr("a < b && c == d || !e")
    assert isinstance(node, N.Logical) and node.operator == "||"
    assert isinstance(node.left, N.Logical) and node.left.operator == "&&"
    assert isinstance(node.right, N.Unary) and node.right.operator == "!"


def test_postfix_chain():
    node = expr("a.b[0](1, 2)")
    assert isinstance(node, N.Call) and len(node.arguments) == 2
    assert isinstance(node.callee, N.Index)
    assert isinstance(node.callee.target, N.Property) and node.callee.target.name == "b"


def test_postfix_call_must_start_on_the_same_line():
    program = parse("let a = [1, 2]\n[3]")
    assert isinstance(program.body[0], N.Let)
    assert isinstance(program.body[0].value, N.ArrayLiteral)
    assert isinstance(program.body[1], N.ExpressionStatement)
    assert isinstance(program.body[1].expression, N.ArrayLiteral)


def test_property_access_may_continue_on_the_next_line():
    node = expr("a\n  .b\n  .c")
    assert isinstance(node, N.Property) and node.name == "c"


def test_object_literal_keys():
    node = expr('{name: 1, "quoted key": 2, in: 3}')
    assert isinstance(node, N.ObjectLiteral)
    assert [k for k, _ in node.entries] == ["name", "quoted key", "in"]


def test_bare_return_at_end_of_line():
    program = parse("function f() {\n  return\n  1\n}")
    body = program.body[0].body.statements
    assert isinstance(body[0], N.Return) and body[0].value is None
    assert isinstance(body[1], N.ExpressionStatement)


def test_else_if_chain():
    program = parse("if a { } else if b { } else { }")
    node = program.body[0]
    assert isinstance(node, N.If)
    assert isinstance(node.else_branch, N.If)
    assert isinstance(node.else_branch.else_branch, N.Block)


def test_function_declaration_with_types():
    program = parse("adapt function f(a: float, b: int) -> float { return a }")
    decl = program.body[0]
    assert isinstance(decl, N.FunctionDecl) and decl.adapt is True
    assert [(p.name, p.type_name) for p in decl.parameters] == [("a", "float"), ("b", "int")]
    assert decl.return_type == "float"


def test_mycelium_declaration():
    source = """
    mycelium Net {
        signal rate: float = 0.5
        signal tag: string
        network links { nodes: 3, density: 0.5 }
        network topo: Topology
        function grow() { }
        adapt function react() { }
    }
    """
    decl = parse(source).body[0]
    assert isinstance(decl, N.MyceliumDecl)
    assert [f.name for f in decl.fields] == ["rate", "tag", "links", "topo"]
    assert decl.fields[2].entries is not None and decl.fields[3].type_name == "Topology"
    assert [m.name for m in decl.methods] == ["grow", "react"]
    assert decl.methods[1].adapt is True


def test_top_level_network_and_signal_declarations():
    program = parse('network Topo { nodes: 4 }\nsignal Pulse { amplitude: float, speed: float }')
    assert isinstance(program.body[0], N.NetworkDecl)
    assert isinstance(program.body[1], N.SignalDecl)
    assert program.body[1].fields == [("amplitude", "float"), ("speed", "float")]


def test_environment_declaration_allows_trailing_comma():
    program = parse("environment { temperature: 22.5, humidity: 85.0, }")
    assert [k for k, _ in program.body[0].entries] == ["temperature", "humidity"]


def test_new_with_and_without_parentheses():
    assert isinstance(expr("new Net()"), N.New)
    assert isinstance(expr("new Net"), N.New)


@pytest.mark.parametrize("source, message", [
    ("1 = 2", "Invalid assignment target"),
    ("function main() {\n print(1)\n", "Unterminated function 'main'"),
    ("let = 5", "Expected variable name after 'let'"),
    ("if x { } else if { }", "Expected '{' to start if body, found end of file"),
    ("print(1", "Expected ')' after arguments, found end of file"),
    ("[1, 2", "Expected ',' or ']' in array literal, found end of file"),
    ("[1, 2,", "Unterminated array literal"),
    ("let a = {x 1}", "Expected ':' after key 'x'"),
    ("else { }", "'else' without a matching 'if'"),
    ("function f() { function g() { } }", "only allowed at the top level"),
    ("for x { }", "Expected 'in' after loop variable 'x'"),
    ("mycelium M { let a = 1 }", "Expected 'signal', 'network' or 'function' inside mycelium 'M'"),
    ("mycelium M { signal a }", "needs a type or a default value"),
])
def test_syntax_errors(source, message):
    with pytest.raises(MyceliumSyntaxError) as info:
        parse(source)
    assert message in str(info.value)


def test_syntax_error_carries_line_number():
    with pytest.raises(MyceliumSyntaxError) as info:
        parse("let a = 1\nlet b = 2\nlet c = )")
    assert info.value.line == 3
