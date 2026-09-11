"""Tree-walking interpreter for Mycelium-EI-Lang."""

from __future__ import annotations

import copy
import os
import random
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from . import nodes as N
from .errors import MyceliumError, MyceliumRuntimeError
from .parser import parse
from .values import Builtin, Function, MyceliumClass, MyceliumInstance, format_value, truthy, type_name

# Nested Mycelium function calls allowed by default. Each language call costs
# 7 to 22 Python frames (measured), and CPython 3.10 overflows its C stack
# somewhere between 5000 and 8000 frames on an 8 MB main-thread stack, so the
# default keeps the derived recursion limit near 4000. ``run_in_thread`` gives
# a bigger stack; the ``myc`` command uses it with a cap of 2000.
MAX_CALL_DEPTH = 200
PYTHON_FRAMES_PER_CALL = 18
RECURSION_HEADROOM = 400
CLI_MAX_CALL_DEPTH = 2000
CLI_STACK_BYTES = 256 * 1024 * 1024


class ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value


class Environment:
    """A lexical scope. ``values`` may be shared with a mycelium instance's fields."""

    __slots__ = ("values", "constants", "parent")

    def __init__(self, parent: Optional["Environment"] = None, values: Optional[Dict[str, Any]] = None):
        self.values: Dict[str, Any] = values if values is not None else {}
        self.constants: set = set()
        self.parent = parent

    def define(self, name: str, value: Any, constant: bool = False) -> None:
        self.values[name] = value
        if constant:
            self.constants.add(name)
        else:
            self.constants.discard(name)

    def resolve(self, name: str) -> Optional["Environment"]:
        if name in self.values:
            return self
        return self.parent.resolve(name) if self.parent is not None else None

    def lookup(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent is None:
            raise KeyError(name)
        return self.parent.lookup(name)

    def assign(self, name: str, value: Any) -> bool:
        if name in self.values:
            if name in self.constants:
                raise MyceliumRuntimeError(f"Cannot assign to constant '{name}'")
            self.values[name] = value
            return True
        if self.parent is None:
            return False
        return self.parent.assign(name, value)


class InstanceEnvironment(Environment):
    """Scope of a mycelium instance: its fields, then its methods, then globals."""

    __slots__ = ("instance", "interpreter")

    def __init__(self, instance: MyceliumInstance, interpreter: "Interpreter", parent: Environment):
        super().__init__(parent, instance.fields)
        self.instance = instance
        self.interpreter = interpreter

    def resolve(self, name: str) -> Optional[Environment]:
        if name in self.values:
            return self
        if name in self.instance.cls.methods:
            return self
        return self.parent.resolve(name) if self.parent else None

    def lookup(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if name in self.instance.cls.methods:
            return self.interpreter.bound_method(self.instance, name)
        if self.parent is None:
            raise KeyError(name)
        return self.parent.lookup(name)

    def assign(self, name: str, value: Any) -> bool:
        if name in self.values:
            self.values[name] = value
            return True
        if name in self.instance.cls.methods:
            raise MyceliumRuntimeError(f"Cannot assign to method '{name}' of mycelium '{self.instance.cls.name}'")
        return self.parent.assign(name, value) if self.parent else False


ZERO_VALUES = {"float": 0.0, "int": 0, "string": "", "str": "", "bool": False, "array": [], "object": {}}


class Interpreter:
    """Executes a parsed ``Program``.

    ``write`` receives every line printed by the program (defaults to stdout).
    ``no_sleep`` turns ``sleep()`` into a no-op; the ``MYCELIUM_NO_SLEEP=1``
    environment variable does the same.
    """

    def __init__(self, filename: str = "<string>", write: Optional[Callable[[str], None]] = None,
                 no_sleep: Optional[bool] = None, seed: Optional[int] = None,
                 max_call_depth: int = MAX_CALL_DEPTH):
        self.filename = filename
        self.max_call_depth = max_call_depth
        self.write = write or self._default_write
        if no_sleep is None:
            no_sleep = os.environ.get("MYCELIUM_NO_SLEEP", "") not in ("", "0")
        self.no_sleep = no_sleep
        if seed is not None:
            random.seed(seed)

        self.globals = Environment()
        self.environment_params: Dict[str, Any] = {}
        self.classes: Dict[str, MyceliumClass] = {}
        self.network_records: Dict[str, Dict[str, Any]] = {}
        self.signal_types: Dict[str, List[tuple]] = {}
        self.instances: List[MyceliumInstance] = []
        self.adapt_functions: List[Function] = []
        self._adapting = False
        self._network = None
        self._bio_optimizer = None
        self._bio_ml = None
        self._cultivation = None
        self.call_depth = 0

        from .builtins import install_builtins
        install_builtins(self)

        self._exec = {
            N.EnvironmentDecl: self._exec_environment,
            N.FunctionDecl: self._exec_function_decl,
            N.MyceliumDecl: self._exec_mycelium_decl,
            N.NetworkDecl: self._exec_network_decl,
            N.SignalDecl: self._exec_signal_decl,
            N.Let: self._exec_let,
            N.If: self._exec_if,
            N.While: self._exec_while,
            N.For: self._exec_for,
            N.Return: self._exec_return,
            N.ExpressionStatement: self._exec_expression_statement,
            N.Block: self._exec_block,
        }
        self._eval = {
            N.Literal: lambda node, env: node.value,
            N.Identifier: self._eval_identifier,
            N.ArrayLiteral: self._eval_array,
            N.ObjectLiteral: self._eval_object,
            N.Unary: self._eval_unary,
            N.Binary: self._eval_binary,
            N.Logical: self._eval_logical,
            N.Call: self._eval_call,
            N.Index: self._eval_index,
            N.Property: self._eval_property,
            N.Assign: self._eval_assign,
            N.New: self._eval_new,
        }

    @staticmethod
    def _default_write(text: str) -> None:
        sys.stdout.write(text + "\n")

    # -- entry points ----------------------------------------------------

    def run(self, source: str) -> Any:
        """Parse and execute ``source``. Runs ``main()`` last if it is defined."""
        program = parse(source, self.filename)
        return self.execute(program)

    def execute(self, program: N.Program) -> Any:
        old_limit = sys.getrecursionlimit()
        needed = self.max_call_depth * PYTHON_FRAMES_PER_CALL + RECURSION_HEADROOM
        if old_limit < needed:
            sys.setrecursionlimit(needed)
        try:
            for node in program.body:
                self.exec_node(node, self.globals)
            main = self.globals.values.get("main")
            if isinstance(main, Function):
                return self.call_function(main, [], program)
            return None
        finally:
            if old_limit < needed:
                sys.setrecursionlimit(old_limit)

    # -- error helpers ---------------------------------------------------

    def error(self, message: str, node: Optional[N.Node] = None) -> MyceliumRuntimeError:
        line = node.line if node is not None else None
        column = node.column if node is not None else None
        return MyceliumRuntimeError(message, line, column, self.filename)

    def _locate(self, err: MyceliumError, node: Optional[N.Node]) -> MyceliumError:
        if node is None:
            return err
        if err.line is None:
            err.line, err.column = node.line, node.column
        if err.filename is None:
            err.filename = self.filename
        return err

    # -- statements ------------------------------------------------------

    def exec_node(self, node: Any, env: Environment) -> None:
        handler = self._exec.get(type(node))
        if handler is None:
            raise self.error(f"Cannot execute node of type {type(node).__name__}", node)
        handler(node, env)

    def _exec_environment(self, node: N.EnvironmentDecl, env: Environment) -> None:
        for key, expr in node.entries:
            self.environment_params[key] = self.evaluate(expr, env)

    def _exec_function_decl(self, node: N.FunctionDecl, env: Environment) -> None:
        function = Function(node, env)
        env.define(node.name, function)
        if node.adapt:
            self.adapt_functions.append(function)

    def _exec_mycelium_decl(self, node: N.MyceliumDecl, env: Environment) -> None:
        cls = MyceliumClass(node)
        self.classes[node.name] = cls
        env.define(node.name, cls)

    def _exec_network_decl(self, node: N.NetworkDecl, env: Environment) -> None:
        record = {key: self.evaluate(expr, env) for key, expr in node.entries}
        self.network_records[node.name] = record
        env.define(node.name, record)

    def _exec_signal_decl(self, node: N.SignalDecl, env: Environment) -> None:
        self.signal_types[node.name] = list(node.fields)

    def _exec_let(self, node: N.Let, env: Environment) -> None:
        value = self.evaluate(node.value, env)
        env.define(node.name, value, node.constant)

    def _exec_if(self, node: N.If, env: Environment) -> None:
        if truthy(self.evaluate(node.condition, env)):
            self._exec_block(node.then_branch, env)
        elif node.else_branch is not None:
            if isinstance(node.else_branch, N.If):
                self._exec_if(node.else_branch, env)
            else:
                self._exec_block(node.else_branch, env)

    def _exec_while(self, node: N.While, env: Environment) -> None:
        while truthy(self.evaluate(node.condition, env)):
            self._exec_block(node.body, env)

    def _exec_for(self, node: N.For, env: Environment) -> None:
        iterable = self.evaluate(node.iterable, env)
        for item in self.iterate(iterable, node.iterable):
            scope = Environment(env)
            scope.define(node.variable, item)
            self._exec_statements(node.body.statements, scope)

    def _exec_return(self, node: N.Return, env: Environment) -> None:
        value = self.evaluate(node.value, env) if node.value is not None else None
        raise ReturnSignal(value)

    def _exec_expression_statement(self, node: N.ExpressionStatement, env: Environment) -> None:
        self.evaluate(node.expression, env)

    def _exec_block(self, node: N.Block, env: Environment) -> None:
        self._exec_statements(node.statements, Environment(env))

    def _exec_statements(self, statements: List[Any], env: Environment) -> None:
        for statement in statements:
            self.exec_node(statement, env)

    def iterate(self, value: Any, node: N.Node):
        if isinstance(value, (list, tuple)):
            return list(value)
        if isinstance(value, dict):
            return list(value.keys())
        if isinstance(value, str):
            return list(value)
        if isinstance(value, bool):
            raise self.error("Cannot iterate over a bool", node)
        if isinstance(value, int):
            return range(value)
        if value is None:
            raise self.error("Cannot iterate over null", node)
        if hasattr(value, "__iter__"):
            return list(value)
        raise self.error(f"Cannot iterate over a value of type {type_name(value)}", node)

    # -- expressions -----------------------------------------------------

    def evaluate(self, node: Any, env: Environment) -> Any:
        handler = self._eval.get(type(node))
        if handler is None:
            raise self.error(f"Cannot evaluate node of type {type(node).__name__}", node)
        return handler(node, env)

    def _eval_identifier(self, node: N.Identifier, env: Environment) -> Any:
        try:
            return env.lookup(node.name)
        except KeyError:
            if node.name in self.environment_params:
                raise self.error(
                    f"Undefined variable '{node.name}' (use get_env(\"{node.name}\") to read an environment parameter)",
                    node)
            raise self.error(f"Undefined variable '{node.name}'", node)

    def _eval_array(self, node: N.ArrayLiteral, env: Environment) -> list:
        return [self.evaluate(element, env) for element in node.elements]

    def _eval_object(self, node: N.ObjectLiteral, env: Environment) -> dict:
        return {key: self.evaluate(expr, env) for key, expr in node.entries}

    def _eval_unary(self, node: N.Unary, env: Environment) -> Any:
        operand = self.evaluate(node.operand, env)
        if node.operator == "!":
            return not truthy(operand)
        if isinstance(operand, bool) or not isinstance(operand, (int, float)):
            raise self.error(f"Unary '-' needs a number, got {type_name(operand)}", node)
        return -operand

    def _eval_logical(self, node: N.Logical, env: Environment) -> Any:
        left = self.evaluate(node.left, env)
        if node.operator == "||":
            return left if truthy(left) else self.evaluate(node.right, env)
        return self.evaluate(node.right, env) if truthy(left) else left

    def _eval_binary(self, node: N.Binary, env: Environment) -> Any:
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        op = node.operator
        try:
            if op == "+":
                if isinstance(left, str) or isinstance(right, str):
                    return format_value(left) + format_value(right)
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                self._check_numbers(left, right, op, node)
                return left + right
            if op == "-":
                self._check_numbers(left, right, op, node)
                return left - right
            if op == "*":
                if isinstance(left, str) and isinstance(right, int) and not isinstance(right, bool):
                    return left * right
                if isinstance(left, list) and isinstance(right, int) and not isinstance(right, bool):
                    return left * right
                self._check_numbers(left, right, op, node)
                return left * right
            if op == "/":
                self._check_numbers(left, right, op, node)
                if right == 0:
                    raise self.error("Division by zero", node)
                return left / right
            if op == "%":
                self._check_numbers(left, right, op, node)
                if right == 0:
                    raise self.error("Modulo by zero", node)
                return left % right
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op in ("<", ">", "<=", ">="):
                self._check_comparable(left, right, op, node)
                if op == "<":
                    return left < right
                if op == ">":
                    return left > right
                if op == "<=":
                    return left <= right
                return left >= right
        except MyceliumError:
            raise
        except (TypeError, ValueError, OverflowError) as exc:
            raise self.error(f"Cannot apply '{op}' to {type_name(left)} and {type_name(right)}: {exc}", node)
        raise self.error(f"Unknown operator '{op}'", node)

    @staticmethod
    def _is_number(value: Any) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def _check_numbers(self, left: Any, right: Any, op: str, node: N.Node) -> None:
        if not (self._is_number(left) and self._is_number(right)):
            raise self.error(f"Cannot apply '{op}' to {type_name(left)} and {type_name(right)}", node)

    def _check_comparable(self, left: Any, right: Any, op: str, node: N.Node) -> None:
        if self._is_number(left) and self._is_number(right):
            return
        if isinstance(left, str) and isinstance(right, str):
            return
        raise self.error(f"Cannot compare {type_name(left)} and {type_name(right)} with '{op}'", node)

    def _eval_call(self, node: N.Call, env: Environment) -> Any:
        callee_node = node.callee
        if isinstance(callee_node, N.Identifier):
            try:
                callee = env.lookup(callee_node.name)
            except KeyError:
                raise self.error(f"Undefined function '{callee_node.name}'", node)
        else:
            callee = self.evaluate(callee_node, env)
        arguments = [self.evaluate(argument, env) for argument in node.arguments]
        return self.call_value(callee, arguments, node)

    def call_value(self, callee: Any, arguments: List[Any], node: N.Node) -> Any:
        if isinstance(callee, Function):
            return self.call_function(callee, arguments, node)
        if isinstance(callee, Builtin):
            try:
                return callee.func(*arguments)
            except MyceliumError as err:
                raise self._locate(err, node)
            except ReturnSignal:
                raise
            except RecursionError:
                raise self.error("Maximum recursion depth exceeded", node)
            except Exception as exc:  # noqa: BLE001 - surface Python errors as language errors
                raise self.error(f"{callee.name}(): {exc}", node)
        if isinstance(callee, MyceliumClass):
            return self.instantiate(callee, arguments, node)
        if callable(callee):
            try:
                return callee(*arguments)
            except MyceliumError as err:
                raise self._locate(err, node)
            except Exception as exc:  # noqa: BLE001
                raise self.error(f"{getattr(callee, '__name__', 'call')}(): {exc}", node)
        raise self.error(f"Value of type {type_name(callee)} is not callable", node)

    def call_function(self, function: Function, arguments: List[Any], node: N.Node) -> Any:
        decl = function.decl
        if len(arguments) != len(decl.parameters):
            raise self.error(
                f"Function '{function.name}' expects {len(decl.parameters)} argument(s), got {len(arguments)}", node)
        if function.instance is not None:
            parent: Environment = InstanceEnvironment(function.instance, self, function.closure)
        else:
            parent = function.closure
        scope = Environment(parent)
        for parameter, value in zip(decl.parameters, arguments):
            scope.define(parameter.name, value)
        if self.call_depth >= self.max_call_depth:
            raise self.error(
                f"Maximum call depth ({self.max_call_depth}) exceeded in function '{function.name}'", node)
        self.call_depth += 1
        try:
            self._exec_statements(decl.body.statements, scope)
        except ReturnSignal as signal:
            return signal.value
        except RecursionError:
            raise self.error(f"Expression nesting too deep in function '{function.name}'", node)
        finally:
            self.call_depth -= 1
        return None

    def bound_method(self, instance: MyceliumInstance, name: str) -> Function:
        decl = instance.cls.methods[name]
        return Function(decl, self.globals, instance)

    def _eval_new(self, node: N.New, env: Environment) -> MyceliumInstance:
        cls = self.classes.get(node.class_name)
        if cls is None:
            raise self.error(f"Unknown mycelium '{node.class_name}'", node)
        arguments = [self.evaluate(argument, env) for argument in node.arguments]
        return self.instantiate(cls, arguments, node)

    def instantiate(self, cls: MyceliumClass, arguments: List[Any], node: N.Node) -> MyceliumInstance:
        instance = MyceliumInstance(cls)
        for field in cls.fields:
            instance.fields[field.name] = self._field_default(field, node)
        self.instances.append(instance)
        if "init" in cls.methods:
            self.call_function(self.bound_method(instance, "init"), arguments, node)
        elif arguments:
            raise self.error(
                f"Mycelium '{cls.name}' has no 'init' function, so 'new {cls.name}' takes no arguments", node)
        return instance

    def _field_default(self, field: N.FieldDecl, node: N.Node) -> Any:
        if field.entries is not None:
            return {key: self.evaluate(expr, self.globals) for key, expr in field.entries}
        if field.default is not None:
            return self.evaluate(field.default, self.globals)
        type_name_ = field.type_name or ""
        if type_name_ in self.network_records:
            return copy.deepcopy(self.network_records[type_name_])
        if type_name_ in self.signal_types:
            return {name: self._zero(ftype) for name, ftype in self.signal_types[type_name_]}
        return self._zero(type_name_)

    @staticmethod
    def _zero(type_name_: str) -> Any:
        if type_name_.endswith("[]"):
            return []
        value = ZERO_VALUES.get(type_name_)
        return copy.copy(value) if value is not None else None

    def _eval_index(self, node: N.Index, env: Environment) -> Any:
        target = self.evaluate(node.target, env)
        index = self.evaluate(node.index, env)
        if isinstance(target, (list, tuple, str)):
            if not isinstance(index, int) or isinstance(index, bool):
                raise self.error(f"Array index must be an int, got {type_name(index)}", node)
            if index >= len(target) or index < -len(target):
                raise self.error(f"Index {index} out of range for {type_name(target)} of length {len(target)}", node)
            return target[index]
        if isinstance(target, dict):
            try:
                return target[index]
            except (KeyError, TypeError):
                raise self.error(f"Key {format_value(index, True)} not found in object", node)
        if isinstance(target, MyceliumInstance):
            if index in target.fields:
                return target.fields[index]
            raise self.error(f"Mycelium '{target.cls.name}' has no field {format_value(index, True)}", node)
        raise self.error(f"Cannot index a value of type {type_name(target)}", node)

    def _eval_property(self, node: N.Property, env: Environment) -> Any:
        target = self.evaluate(node.target, env)
        return self.get_property(target, node.name, node)

    def get_property(self, target: Any, name: str, node: N.Node) -> Any:
        from .builtins import member_method
        if isinstance(target, dict):
            if name in target:
                return target[name]
            method = member_method(self, target, name)
            return method if method is not None else None
        if isinstance(target, MyceliumInstance):
            if name in target.fields:
                return target.fields[name]
            if name in target.cls.methods:
                return self.bound_method(target, name)
            raise self.error(f"Mycelium '{target.cls.name}' has no field or function '{name}'", node)
        if isinstance(target, (list, str)):
            method = member_method(self, target, name)
            if method is None:
                raise self.error(f"{type_name(target)} has no property '{name}'", node)
            return method
        if target is None:
            raise self.error(f"Cannot read property '{name}' of null", node)
        if isinstance(target, (bool, int, float, Function, Builtin, MyceliumClass)):
            raise self.error(f"{type_name(target)} has no property '{name}'", node)
        if name.startswith("_"):
            raise self.error(f"Property '{name}' is not accessible", node)
        try:
            return getattr(target, name)
        except AttributeError:
            raise self.error(f"{type_name(target)} has no property '{name}'", node)

    def _eval_assign(self, node: N.Assign, env: Environment) -> Any:
        value = self.evaluate(node.value, env)
        target = node.target
        if isinstance(target, N.Identifier):
            try:
                assigned = env.assign(target.name, value)
            except MyceliumError as err:
                raise self._locate(err, node)
            if not assigned:
                raise self.error(
                    f"Cannot assign to undefined variable '{target.name}' (declare it first with 'let')", node)
            return value
        if isinstance(target, N.Index):
            container = self.evaluate(target.target, env)
            index = self.evaluate(target.index, env)
            if isinstance(container, list):
                if not isinstance(index, int) or isinstance(index, bool):
                    raise self.error(f"Array index must be an int, got {type_name(index)}", node)
                if index >= len(container) or index < -len(container):
                    raise self.error(f"Index {index} out of range for array of length {len(container)}", node)
                container[index] = value
                return value
            if isinstance(container, dict):
                container[index] = value
                return value
            if isinstance(container, MyceliumInstance) and isinstance(index, str):
                container.fields[index] = value
                return value
            raise self.error(f"Cannot assign into a value of type {type_name(container)}", node)
        if isinstance(target, N.Property):
            container = self.evaluate(target.target, env)
            if isinstance(container, dict):
                container[target.name] = value
                return value
            if isinstance(container, MyceliumInstance):
                if target.name in container.cls.methods:
                    raise self.error(f"Cannot assign to function '{target.name}' of mycelium '{container.cls.name}'",
                                     node)
                container.fields[target.name] = value
                return value
            raise self.error(f"Cannot set property '{target.name}' on a value of type {type_name(container)}", node)
        raise self.error("Invalid assignment target", node)

    # -- environment parameters and adaptation ---------------------------

    def get_env(self, name: str) -> Any:
        if name not in self.environment_params:
            raise MyceliumRuntimeError(f"Unknown environment parameter '{name}'")
        return self.environment_params[name]

    def set_env(self, name: str, value: Any) -> None:
        self.environment_params[name] = value
        self.trigger_adaptation()

    def trigger_adaptation(self) -> None:
        """Run every ``adapt function`` (top-level and per live instance) once."""
        if self._adapting:
            return
        self._adapting = True
        try:
            for function in list(self.adapt_functions):
                if function.arity == 0:
                    self.call_function(function, [], function.decl)
            for instance in list(self.instances):
                for name in instance.cls.adapt_methods:
                    method = self.bound_method(instance, name)
                    if method.arity == 0:
                        self.call_function(method, [], method.decl)
        finally:
            self._adapting = False

    def sleep(self, milliseconds: Any) -> None:
        if not self._is_number(milliseconds) or milliseconds < 0:
            raise MyceliumRuntimeError("sleep() needs a non-negative number of milliseconds")
        if self.no_sleep:
            return
        time.sleep(milliseconds / 1000.0)

    # -- lazily created subsystems ---------------------------------------

    @property
    def network(self):
        if self._network is None:
            from .network import MyceliumNetwork
            self._network = MyceliumNetwork("Interpreter Network")
        return self._network

    @property
    def bio_optimizer(self):
        if self._bio_optimizer is None:
            from .bio.algorithms import BiologicalOptimizer
            self._bio_optimizer = BiologicalOptimizer()
        return self._bio_optimizer

    @property
    def bio_ml(self):
        if self._bio_ml is None:
            from .bio.ml import BiologicalMLOptimizer
            self._bio_ml = BiologicalMLOptimizer()
        return self._bio_ml

    @property
    def cultivation(self):
        if self._cultivation is None:
            from .bio.cultivation import CultivationMonitoringPlatform
            self._cultivation = CultivationMonitoringPlatform()
        return self._cultivation


def run_in_thread(target: Callable[[], Any], stack_bytes: int = CLI_STACK_BYTES) -> Any:
    """Call ``target`` on a thread with a ``stack_bytes`` stack and return its result.

    Deep recursion in a Mycelium program needs a deeper C stack than the main
    thread has on CPython 3.10 and older. Exceptions propagate to the caller.
    If the platform refuses the stack size, ``target`` runs on the current thread.
    """
    result: Dict[str, Any] = {}

    def runner() -> None:
        try:
            result["value"] = target()
        except BaseException as exc:  # noqa: BLE001 - re-raised below
            result["error"] = exc

    try:
        previous = threading.stack_size(stack_bytes)
    except (ValueError, RuntimeError):
        return target()
    try:
        thread = threading.Thread(target=runner, name="mycelium-program", daemon=True)
        thread.start()
    finally:
        threading.stack_size(previous)
    thread.join()
    if "error" in result:
        raise result["error"]
    return result.get("value")


def run_source(source: str, filename: str = "<string>", **options: Any) -> Interpreter:
    """Run ``source`` and return the interpreter that ran it."""
    interpreter = Interpreter(filename, **options)
    interpreter.run(source)
    return interpreter


def run_file(path: str, **options: Any) -> Interpreter:
    """Run the program stored at ``path`` and return the interpreter that ran it."""
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    return run_source(source, path, **options)
