"""Abstract syntax tree node types produced by the parser.

Every node carries the ``line`` and ``column`` of its first token so the
interpreter can report where a runtime error happened.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


@dataclass
class Node:
    line: int
    column: int


# -- expressions -----------------------------------------------------------

@dataclass
class Literal(Node):
    value: Any


@dataclass
class Identifier(Node):
    name: str


@dataclass
class ArrayLiteral(Node):
    elements: List["Expr"]


@dataclass
class ObjectLiteral(Node):
    entries: List[Tuple[str, "Expr"]]


@dataclass
class Unary(Node):
    operator: str
    operand: "Expr"


@dataclass
class Binary(Node):
    left: "Expr"
    operator: str
    right: "Expr"


@dataclass
class Logical(Node):
    left: "Expr"
    operator: str  # "&&" or "||"
    right: "Expr"


@dataclass
class Call(Node):
    callee: "Expr"
    arguments: List["Expr"]


@dataclass
class Index(Node):
    target: "Expr"
    index: "Expr"


@dataclass
class Property(Node):
    target: "Expr"
    name: str


@dataclass
class Assign(Node):
    target: "Expr"  # Identifier, Index or Property
    value: "Expr"


@dataclass
class New(Node):
    class_name: str
    arguments: List["Expr"]


Expr = Any  # one of the classes above


# -- statements ------------------------------------------------------------

@dataclass
class Let(Node):
    name: str
    type_name: Optional[str]
    value: Expr
    constant: bool = False


@dataclass
class If(Node):
    condition: Expr
    then_branch: "Block"
    else_branch: Optional[Any]  # Block or If


@dataclass
class While(Node):
    condition: Expr
    body: "Block"


@dataclass
class For(Node):
    variable: str
    iterable: Expr
    body: "Block"


@dataclass
class Return(Node):
    value: Optional[Expr]


@dataclass
class ExpressionStatement(Node):
    expression: Expr


@dataclass
class Block(Node):
    statements: List[Any]


Stmt = Any


# -- declarations ----------------------------------------------------------

@dataclass
class Parameter:
    name: str
    type_name: Optional[str]


@dataclass
class FunctionDecl(Node):
    name: str
    parameters: List[Parameter]
    return_type: Optional[str]
    body: Block
    adapt: bool = False


@dataclass
class EnvironmentDecl(Node):
    entries: List[Tuple[str, Expr]]


@dataclass
class NetworkDecl(Node):
    """``network Name { key: value, ... }`` at top level: a named record."""
    name: str
    entries: List[Tuple[str, Expr]]


@dataclass
class SignalDecl(Node):
    """``signal Name { field: type, ... }`` at top level: a record type."""
    name: str
    fields: List[Tuple[str, str]]


@dataclass
class FieldDecl(Node):
    """A ``signal`` or ``network`` member inside a ``mycelium`` block."""
    name: str
    type_name: Optional[str]
    default: Optional[Expr]
    entries: Optional[List[Tuple[str, Expr]]] = None  # inline network record


@dataclass
class MyceliumDecl(Node):
    name: str
    fields: List[FieldDecl] = field(default_factory=list)
    methods: List[FunctionDecl] = field(default_factory=list)


@dataclass
class Program(Node):
    body: List[Any]
