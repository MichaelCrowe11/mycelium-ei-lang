"""Runtime value types and formatting helpers."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from . import nodes as N


class MyceliumClass:
    """A ``mycelium Name { ... }`` declaration."""

    def __init__(self, decl: N.MyceliumDecl):
        self.decl = decl
        self.name = decl.name
        self.fields: List[N.FieldDecl] = list(decl.fields)
        self.methods: Dict[str, N.FunctionDecl] = {m.name: m for m in decl.methods}
        self.adapt_methods: List[str] = [m.name for m in decl.methods if m.adapt]

    def __repr__(self) -> str:
        return f"<mycelium {self.name}>"


class MyceliumInstance:
    """An object created with ``new Name()``."""

    def __init__(self, cls: MyceliumClass):
        self.cls = cls
        self.fields: Dict[str, Any] = {}

    def __repr__(self) -> str:
        return format_value(self)


class Function:
    """A user-defined function, optionally bound to a mycelium instance."""

    def __init__(self, decl: N.FunctionDecl, closure: Any, instance: Optional[MyceliumInstance] = None):
        self.decl = decl
        self.name = decl.name
        self.closure = closure
        self.instance = instance

    @property
    def arity(self) -> int:
        return len(self.decl.parameters)

    def bind(self, instance: MyceliumInstance) -> "Function":
        return Function(self.decl, self.closure, instance)

    def __repr__(self) -> str:
        if self.instance is not None:
            return f"<method {self.instance.cls.name}.{self.name}>"
        return f"<function {self.name}>"


class Builtin:
    """A function implemented in Python and exposed to programs."""

    def __init__(self, name: str, func: Callable[..., Any], doc: str = ""):
        self.name = name
        self.func = func
        self.doc = doc

    def __call__(self, *args: Any) -> Any:
        return self.func(*args)

    def __repr__(self) -> str:
        return f"<builtin {self.name}>"


def type_name(value: Any) -> str:
    """The language-level type name of a runtime value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, MyceliumInstance):
        return value.cls.name
    if isinstance(value, MyceliumClass):
        return "mycelium"
    if isinstance(value, (Function, Builtin)) or callable(value):
        return "function"
    return type(value).__name__


def _is_identifier(key: Any) -> bool:
    return isinstance(key, str) and key.isidentifier()


def format_value(value: Any, nested: bool = False) -> str:
    """Render a value the way ``print`` shows it.

    Strings print bare at the top level and quoted inside arrays and objects.
    Booleans print as ``true``/``false`` and ``None`` as ``null``.
    """
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        if nested:
            return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        return value
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(format_value(v, True) for v in value) + "]"
    if isinstance(value, tuple):
        return "[" + ", ".join(format_value(v, True) for v in value) + "]"
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            key_text = key if _is_identifier(key) else format_value(key, True)
            parts.append(f"{key_text}: {format_value(item, True)}")
        return "{" + ", ".join(parts) + "}"
    if isinstance(value, MyceliumInstance):
        inner = ", ".join(f"{k}: {format_value(v, True)}" for k, v in value.fields.items())
        return f"{value.cls.name} {{{inner}}}"
    return str(value)


def truthy(value: Any) -> bool:
    return bool(value)
