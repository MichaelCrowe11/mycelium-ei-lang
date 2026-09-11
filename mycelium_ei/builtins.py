"""Built-in functions available to every Mycelium program."""

from __future__ import annotations

import math
import random
import time
from typing import Any, Callable, Dict, List, Optional

from .errors import MyceliumRuntimeError
from .values import Builtin, Function, MyceliumInstance, format_value, type_name


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _need_number(name: str, value: Any, what: str = "a number") -> Any:
    if not _is_number(value):
        raise MyceliumRuntimeError(f"{name}() needs {what}, got {type_name(value)}")
    return value


def _need_int(name: str, value: Any, what: str = "an int") -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        raise MyceliumRuntimeError(f"{name}() needs {what}, got {type_name(value)}")
    return value


def _need_string(name: str, value: Any, what: str = "a string") -> str:
    if not isinstance(value, str):
        raise MyceliumRuntimeError(f"{name}() needs {what}, got {type_name(value)}")
    return value


def _need_list(name: str, value: Any, what: str = "an array") -> list:
    if not isinstance(value, list):
        raise MyceliumRuntimeError(f"{name}() needs {what}, got {type_name(value)}")
    return value


def _need_dict(name: str, value: Any, what: str = "an object") -> dict:
    if not isinstance(value, dict):
        raise MyceliumRuntimeError(f"{name}() needs {what}, got {type_name(value)}")
    return value


# ---------------------------------------------------------------------------
# Member methods on arrays, strings and objects: ``list.append(x)`` etc.
# ---------------------------------------------------------------------------

def member_method(interp, target: Any, name: str) -> Any:
    """Return a bound ``Builtin`` (or a plain value for ``length``) or ``None``."""
    if name == "length" and isinstance(target, (list, str, dict)):
        return len(target)
    table = None
    if isinstance(target, list):
        table = _LIST_METHODS
    elif isinstance(target, str):
        table = _STRING_METHODS
    elif isinstance(target, dict):
        table = _DICT_METHODS
    if table is None or name not in table:
        return None
    func = table[name]
    return Builtin(name, lambda *args: func(interp, target, *args))


def _list_append(interp, target: list, *values: Any) -> None:
    if not values:
        raise MyceliumRuntimeError("append() needs at least one value")
    target.extend(values)


def _list_pop(interp, target: list, index: Any = -1) -> Any:
    if not target:
        raise MyceliumRuntimeError("pop() on an empty array")
    index = _need_int("pop", index, "an int index")
    if index >= len(target) or index < -len(target):
        raise MyceliumRuntimeError(f"pop(): index {index} out of range for array of length {len(target)}")
    return target.pop(index)


def _list_insert(interp, target: list, index: Any, value: Any) -> None:
    target.insert(_need_int("insert", index, "an int index"), value)


def _list_remove(interp, target: list, value: Any) -> None:
    if value not in target:
        raise MyceliumRuntimeError(f"remove(): {format_value(value, True)} is not in the array")
    target.remove(value)


def _list_contains(interp, target: list, value: Any) -> bool:
    return value in target


def _list_index_of(interp, target: list, value: Any) -> int:
    return target.index(value) if value in target else -1


def _list_sort(interp, target: list) -> None:
    try:
        target.sort()
    except TypeError:
        raise MyceliumRuntimeError("sort(): array holds values that cannot be compared with each other")


def _list_reverse(interp, target: list) -> None:
    target.reverse()


def _list_join(interp, target: list, separator: Any = ", ") -> str:
    return _need_string("join", separator, "a separator string").join(format_value(v) for v in target)


def _list_slice(interp, target: list, start: Any, end: Any = None) -> list:
    start = _need_int("slice", start, "an int start")
    end = len(target) if end is None else _need_int("slice", end, "an int end")
    return target[start:end]


def _list_copy(interp, target: list) -> list:
    return list(target)


_LIST_METHODS: Dict[str, Callable[..., Any]] = {
    "append": _list_append,
    "push": _list_append,
    "pop": _list_pop,
    "insert": _list_insert,
    "remove": _list_remove,
    "contains": _list_contains,
    "index_of": _list_index_of,
    "sort": _list_sort,
    "reverse": _list_reverse,
    "join": _list_join,
    "slice": _list_slice,
    "copy": _list_copy,
}


def _str_split(interp, target: str, separator: Any = None) -> list:
    if separator is None:
        return target.split()
    return target.split(_need_string("split", separator, "a separator string"))


_STRING_METHODS: Dict[str, Callable[..., Any]] = {
    "upper": lambda interp, s: s.upper(),
    "lower": lambda interp, s: s.lower(),
    "trim": lambda interp, s: s.strip(),
    "split": _str_split,
    "contains": lambda interp, s, part: _need_string("contains", part) in s,
    "starts_with": lambda interp, s, part: s.startswith(_need_string("starts_with", part)),
    "ends_with": lambda interp, s, part: s.endswith(_need_string("ends_with", part)),
    "replace": lambda interp, s, old, new: s.replace(_need_string("replace", old), _need_string("replace", new)),
    "index_of": lambda interp, s, part: s.find(_need_string("index_of", part)),
}

_DICT_METHODS: Dict[str, Callable[..., Any]] = {
    "keys": lambda interp, d: list(d.keys()),
    "values": lambda interp, d: list(d.values()),
    "has": lambda interp, d, key: key in d,
    "remove": lambda interp, d, key: d.pop(key, None),
    "copy": lambda interp, d: dict(d),
}


# ---------------------------------------------------------------------------
# Global builtins
# ---------------------------------------------------------------------------

def install_builtins(interp) -> None:
    define = _definer(interp)
    _install_core(interp, define)
    _install_mycelium(interp, define)
    _install_network(interp, define)
    _install_bio(interp, define)


def _definer(interp):
    def define(name: str, doc: str):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            interp.globals.define(name, Builtin(name, func, doc))
            return func
        return decorator
    return define


def _install_core(interp, define) -> None:
    @define("print", "print(values...) writes the values separated by spaces")
    def _print(*args: Any) -> None:
        interp.write(" ".join(format_value(a) for a in args))

    @define("len", "len(value) is the number of items in an array, object or string")
    def _len(value: Any) -> int:
        if isinstance(value, (list, str, dict, tuple)):
            return len(value)
        if isinstance(value, MyceliumInstance):
            return len(value.fields)
        raise MyceliumRuntimeError(f"len() needs an array, object or string, got {type_name(value)}")

    @define("range", "range(end) or range(start, end[, step]) builds an array of ints")
    def _range(*args: Any) -> list:
        if not 1 <= len(args) <= 3:
            raise MyceliumRuntimeError("range() takes 1 to 3 arguments")
        ints = [_need_int("range", a) for a in args]
        if len(ints) == 3 and ints[2] == 0:
            raise MyceliumRuntimeError("range() step must not be zero")
        return list(range(*ints))

    @define("abs", "abs(x) absolute value")
    def _abs(x: Any) -> Any:
        return abs(_need_number("abs", x))

    def _min_max(name: str, func: Callable[..., Any]) -> Callable[..., Any]:
        def inner(*args: Any) -> Any:
            values = args[0] if len(args) == 1 and isinstance(args[0], list) else list(args)
            if not values:
                raise MyceliumRuntimeError(f"{name}() needs at least one value")
            try:
                return func(values)
            except TypeError:
                raise MyceliumRuntimeError(f"{name}(): values cannot be compared with each other")
        return inner

    define("min", "min(a, b, ...) or min(array) smallest value")(_min_max("min", min))
    define("max", "max(a, b, ...) or max(array) largest value")(_min_max("max", max))

    @define("sum", "sum(array) adds the numbers in an array")
    def _sum(values: Any) -> Any:
        values = _need_list("sum", values)
        total: Any = 0
        for v in values:
            total += _need_number("sum", v, "an array of numbers")
        return total

    @define("sqrt", "sqrt(x) square root of a non-negative number")
    def _sqrt(x: Any) -> float:
        _need_number("sqrt", x)
        if x < 0:
            raise MyceliumRuntimeError(f"sqrt() needs a non-negative number, got {format_value(x)}")
        return math.sqrt(x)

    for fname, func in (("sin", math.sin), ("cos", math.cos), ("tan", math.tan),
                        ("exp", math.exp), ("floor", math.floor), ("ceil", math.ceil)):
        def make(fname: str = fname, func: Callable[[float], float] = func) -> None:
            @define(fname, f"{fname}(x)")
            def _math(x: Any) -> Any:
                try:
                    return func(_need_number(fname, x))
                except OverflowError:
                    raise MyceliumRuntimeError(f"{fname}(): result too large for {format_value(x)}")
                except ValueError:
                    raise MyceliumRuntimeError(f"{fname}(): invalid input {format_value(x)}")
        make()

    @define("log", "log(x[, base]) natural logarithm, or logarithm in the given base")
    def _log(x: Any, base: Any = None) -> float:
        _need_number("log", x)
        if x <= 0:
            raise MyceliumRuntimeError("log() needs a positive number")
        if base is None:
            return math.log(x)
        return math.log(x, _need_number("log", base, "a numeric base"))

    @define("pow", "pow(x, y) x raised to the power y")
    def _pow(x: Any, y: Any) -> Any:
        _need_number("pow", x)
        _need_number("pow", y)
        try:
            return math.pow(x, y)
        except OverflowError:
            raise MyceliumRuntimeError(f"pow(): result too large for {format_value(x)} ^ {format_value(y)}")
        except ValueError:
            raise MyceliumRuntimeError(f"pow(): invalid input {format_value(x)} ^ {format_value(y)}")

    @define("round", "round(x[, digits]) round to the nearest int, or to a number of digits")
    def _round(x: Any, digits: Any = None) -> Any:
        _need_number("round", x)
        if digits is None:
            return int(round(x))
        return round(x, _need_int("round", digits, "an int number of digits"))

    @define("random", "random() a float in [0, 1)")
    def _random() -> float:
        return random.random()

    @define("random_range", "random_range(low, high) a float in [low, high]")
    def _random_range(low: Any, high: Any) -> float:
        return random.uniform(_need_number("random_range", low), _need_number("random_range", high))

    @define("random_int", "random_int(low, high) an int in [low, high]")
    def _random_int(low: Any, high: Any) -> int:
        return random.randint(_need_int("random_int", low), _need_int("random_int", high))

    @define("clock", "clock() seconds since the program's process started counting (monotonic)")
    def _clock() -> float:
        return time.perf_counter()

    @define("int", "int(x) convert to int")
    def _int(x: Any) -> int:
        if isinstance(x, bool):
            return int(x)
        if isinstance(x, (int, float)):
            return int(x)
        if isinstance(x, str):
            try:
                return int(x.strip())
            except ValueError:
                raise MyceliumRuntimeError(f"int(): cannot convert \"{x}\" to an int")
        raise MyceliumRuntimeError(f"int(): cannot convert {type_name(x)} to an int")

    @define("float", "float(x) convert to float")
    def _float(x: Any) -> float:
        if isinstance(x, (int, float)):
            return float(x)
        if isinstance(x, str):
            try:
                return float(x.strip())
            except ValueError:
                raise MyceliumRuntimeError(f"float(): cannot convert \"{x}\" to a float")
        raise MyceliumRuntimeError(f"float(): cannot convert {type_name(x)} to a float")

    @define("str", "str(x) convert to string")
    def _str(x: Any) -> str:
        return format_value(x)

    @define("bool", "bool(x) truthiness of a value")
    def _bool(x: Any) -> bool:
        return bool(x)

    @define("type_of", "type_of(x) the type name of a value")
    def _type_of(x: Any) -> str:
        return type_name(x)

    @define("keys", "keys(object) the keys of an object as an array")
    def _keys(value: Any) -> list:
        return list(_need_dict("keys", value).keys())

    @define("values", "values(object) the values of an object as an array")
    def _values(value: Any) -> list:
        return list(_need_dict("values", value).values())

    @define("has", "has(object, key) whether the object has the key")
    def _has(value: Any, key: Any) -> bool:
        return key in _need_dict("has", value)

    @define("contains", "contains(array_or_string, item) membership test")
    def _contains(container: Any, item: Any) -> bool:
        if isinstance(container, str):
            return _need_string("contains", item, "a string to look for") in container
        if isinstance(container, (list, dict)):
            return item in container
        raise MyceliumRuntimeError(f"contains() needs an array, object or string, got {type_name(container)}")

    @define("join", "join(array[, separator]) joins values into a string")
    def _join(values: Any, separator: Any = ", ") -> str:
        return _list_join(interp, _need_list("join", values), separator)

    @define("split", "split(string[, separator]) splits a string into an array")
    def _split(value: Any, separator: Any = None) -> list:
        return _str_split(interp, _need_string("split", value), separator)

    @define("reverse", "reverse(array) a reversed copy of the array")
    def _reverse(value: Any) -> Any:
        if isinstance(value, str):
            return value[::-1]
        return list(reversed(_need_list("reverse", value)))

    @define("sorted", "sorted(array) a sorted copy of the array")
    def _sorted(value: Any) -> list:
        try:
            return sorted(_need_list("sorted", value))
        except TypeError:
            raise MyceliumRuntimeError("sorted(): array holds values that cannot be compared with each other")

    @define("sleep", "sleep(milliseconds) pause the program")
    def _sleep(milliseconds: Any) -> None:
        interp.sleep(milliseconds)

    @define("get_env", "get_env(name) read an environment parameter")
    def _get_env(name: Any) -> Any:
        return interp.get_env(_need_string("get_env", name, "a parameter name"))

    @define("set_env", "set_env(name, value) set an environment parameter and run adapt functions")
    def _set_env(name: Any, value: Any) -> None:
        interp.set_env(_need_string("set_env", name, "a parameter name"), value)

    @define("env", "env() a copy of all environment parameters as an object")
    def _env() -> dict:
        return dict(interp.environment_params)


def _install_mycelium(interp, define) -> None:
    @define("signal_alert", "signal_alert(message) print an alert line")
    def _signal_alert(message: Any) -> None:
        interp.write(f"ALERT: {format_value(message)}")

    @define("signal_network", "signal_network(type, value) print a network signal line")
    def _signal_network(signal_type: Any, value: Any) -> None:
        interp.write(f"Network signal: {format_value(signal_type)} = {format_value(value)}")

    @define("create_one_hot", "create_one_hot(index, size) an array of zeros with a 1.0 at index")
    def _create_one_hot(index: Any, size: Any) -> list:
        index = _need_int("create_one_hot", index)
        size = _need_int("create_one_hot", size)
        result = [0.0] * max(size, 0)
        if 0 <= index < size:
            result[index] = 1.0
        return result

    @define("calculate_growth_factor",
            "calculate_growth_factor(temp, humidity, co2) a 0..1 growth factor around 24 C, 85 percent, 1000 ppm")
    def _growth_factor(temp: Any, humidity: Any, co2: Any) -> float:
        temp = _need_number("calculate_growth_factor", temp)
        humidity = _need_number("calculate_growth_factor", humidity)
        co2 = _need_number("calculate_growth_factor", co2)
        temp_factor = 1.0 - abs(temp - 24.0) / 10.0
        humidity_factor = 1.0 - abs(humidity - 85.0) / 20.0
        co2_factor = min(co2 / 1000.0, 1.0)
        return max(0.0, temp_factor * humidity_factor * co2_factor)

    @define("apply_activation", "apply_activation(x, kind) relu, sigmoid, tanh, softmax (array) or linear")
    def _apply_activation(x: Any, kind: Any) -> Any:
        kind = _need_string("apply_activation", kind, "an activation name")
        if kind == "softmax":
            values = _need_list("apply_activation", x, "an array for softmax")
            numbers = [_need_number("apply_activation", v, "an array of numbers") for v in values]
            if not numbers:
                return []
            peak = max(numbers)
            exps = [math.exp(v - peak) for v in numbers]
            total = sum(exps)
            return [e / total for e in exps]
        x = _need_number("apply_activation", x)
        if kind == "relu":
            return max(0.0, x)
        if kind == "sigmoid":
            if x < -700:
                return 0.0
            return 1.0 / (1.0 + math.exp(-x))
        if kind == "tanh":
            return math.tanh(x)
        if kind == "linear":
            return x
        raise MyceliumRuntimeError(f"apply_activation(): unknown activation \"{kind}\"")

    @define("apply_signal_decay", "apply_signal_decay(signal, distance) multiply by exp(-0.1 * distance)")
    def _apply_signal_decay(signal: Any, distance: Any) -> Any:
        distance = _need_number("apply_signal_decay", distance)
        factor = math.exp(-distance * 0.1)
        if isinstance(signal, list):
            return [_need_number("apply_signal_decay", s, "numbers") * factor for s in signal]
        return _need_number("apply_signal_decay", signal) * factor


def _install_network(interp, define) -> None:
    from .network import MyceliumNetwork, SignalType

    def pick(network: Any) -> MyceliumNetwork:
        if network is None:
            return interp.network
        if isinstance(network, MyceliumNetwork):
            return network
        raise MyceliumRuntimeError(f"expected a network created with create_network(), got {type_name(network)}")

    @define("create_network", "create_network([name]) a new mycelium network")
    def _create_network(name: Any = "MyceliumNetwork") -> MyceliumNetwork:
        network = MyceliumNetwork(_need_string("create_network", name, "a network name"))
        interp.write(f"Created network: {network.name}")
        return network

    @define("add_node", "add_node([network]) add a node, connected to the previous node")
    def _add_node(network: Any = None) -> Any:
        network = pick(network)
        previous = list(network.nodes.values())[-1] if network.nodes else None
        node = network.add_node()
        if previous is not None:
            previous.connect_to(node)
        return node

    @define("connect_nodes", "connect_nodes(a, b) connect two nodes")
    def _connect_nodes(a: Any, b: Any) -> bool:
        if not hasattr(a, "connect_to") or not hasattr(b, "connect_to"):
            raise MyceliumRuntimeError("connect_nodes() needs two nodes from add_node()")
        a.connect_to(b)
        return True

    signal_types = {s.value: s for s in SignalType}

    @define("broadcast_signal", "broadcast_signal(type, payload[, network]) growth, nutrient, stress, alert or data")
    def _broadcast_signal(signal_type: Any, payload: Any, network: Any = None) -> bool:
        kind = _need_string("broadcast_signal", signal_type, "a signal type").lower()
        if kind not in signal_types:
            raise MyceliumRuntimeError(
                f"broadcast_signal(): unknown signal type \"{kind}\" (use {', '.join(signal_types)})")
        pick(network).broadcast_signal(signal_types[kind], _need_dict("broadcast_signal", payload, "a payload object"))
        return True

    @define("update_global_env", "update_global_env(name, value[, network]) set a parameter everywhere")
    def _update_global_env(name: Any, value: Any, network: Any = None) -> bool:
        name = _need_string("update_global_env", name, "a parameter name")
        pick(network).update_environment(name, _need_number("update_global_env", value))
        interp.set_env(name, value)
        return True

    @define("get_network_stats", "get_network_stats([network]) node and connection counts")
    def _get_network_stats(network: Any = None) -> dict:
        return pick(network).get_stats()


def _install_bio(interp, define) -> None:
    def resolve_fitness(name: str, fitness: Any, dimensions: int) -> Callable[[List[float]], float]:
        if isinstance(fitness, str):
            try:
                fitness = interp.globals.lookup(fitness)
            except KeyError:
                raise MyceliumRuntimeError(f"{name}(): unknown function \"{fitness}\"")
        if isinstance(fitness, Function):
            if fitness.arity == 1:
                def call(genes: List[float]) -> Any:
                    return interp.call_value(fitness, [list(genes)], None)
            elif fitness.arity == dimensions:
                def call(genes: List[float]) -> Any:
                    return interp.call_value(fitness, list(genes), None)
            else:
                raise MyceliumRuntimeError(
                    f"{name}(): fitness function '{fitness.name}' takes {fitness.arity} parameter(s); "
                    f"it must take 1 (an array) or {dimensions} (one per dimension)")
        elif isinstance(fitness, Builtin) or callable(fitness):
            def call(genes: List[float]) -> Any:
                return interp.call_value(fitness, list(genes), None)
        else:
            raise MyceliumRuntimeError(f"{name}(): fitness must be a function or a function name, got {type_name(fitness)}")

        def checked(genes: Any) -> float:
            result = call([float(g) for g in genes])
            if not _is_number(result):
                raise MyceliumRuntimeError(f"{name}(): fitness function must return a number, got {type_name(result)}")
            return float(result)
        return checked

    def summary(result: Dict[str, Any], count_key: str) -> dict:
        return {
            "solution": [float(v) for v in result["best_solution"]],
            "fitness": result["best_fitness"],
            count_key: result.get(count_key, 0),
            "time": result["computation_time"],
        }

    @define("genetic_optimize",
            "genetic_optimize(fitness, dimensions=6, population_size=50, max_generations=100) maximise fitness")
    def _genetic(fitness: Any, dimensions: Any = 6, population_size: Any = 50, max_generations: Any = 100) -> dict:
        dimensions = _need_int("genetic_optimize", dimensions)
        result = interp.bio_optimizer.optimize(
            "genetic", resolve_fitness("genetic_optimize", fitness, dimensions), dimensions,
            population_size=_need_int("genetic_optimize", population_size),
            max_generations=_need_int("genetic_optimize", max_generations))
        return summary(result, "generations")

    @define("swarm_optimize",
            "swarm_optimize(fitness, dimensions=6, num_particles=30, max_iterations=100) maximise fitness")
    def _swarm(fitness: Any, dimensions: Any = 6, num_particles: Any = 30, max_iterations: Any = 100) -> dict:
        dimensions = _need_int("swarm_optimize", dimensions)
        result = interp.bio_optimizer.optimize(
            "pso", resolve_fitness("swarm_optimize", fitness, dimensions), dimensions,
            num_particles=_need_int("swarm_optimize", num_particles),
            max_iterations=_need_int("swarm_optimize", max_iterations))
        return summary(result, "iterations")

    @define("ant_optimize", "ant_optimize(fitness, dimensions=6, num_ants=25, max_iterations=100) maximise fitness")
    def _ant(fitness: Any, dimensions: Any = 6, num_ants: Any = 25, max_iterations: Any = 100) -> dict:
        dimensions = _need_int("ant_optimize", dimensions)
        result = interp.bio_optimizer.optimize(
            "aco", resolve_fitness("ant_optimize", fitness, dimensions), dimensions,
            num_ants=_need_int("ant_optimize", num_ants),
            max_iterations=_need_int("ant_optimize", max_iterations))
        return summary(result, "iterations")

    @define("bio_compare", "bio_compare(fitness, dimensions=6) run all three optimizers and compare")
    def _bio_compare(fitness: Any, dimensions: Any = 6) -> dict:
        dimensions = _need_int("bio_compare", dimensions)
        results = interp.bio_optimizer.compare_algorithms(resolve_fitness("bio_compare", fitness, dimensions), dimensions)
        comparison: Dict[str, Any] = {}
        for algorithm, result in results.items():
            if "error" in result:
                comparison[algorithm] = {"error": result["error"]}
            else:
                comparison[algorithm] = {
                    "solution": [float(v) for v in result["best_solution"]],
                    "fitness": result["best_fitness"],
                    "time": result["computation_time"],
                }
        return comparison

    def growth_pattern(samples: int) -> list:
        data = []
        for _ in range(samples):
            temp = random.uniform(-1, 1)
            humidity = random.uniform(-1, 1)
            nutrients = random.uniform(-1, 1)
            ph = random.uniform(-1, 1)
            growth = max(0.0, temp * 0.3 + humidity * 0.4 + nutrients * 0.5)
            branching = max(0.0, nutrients * 0.6 + humidity * 0.2)
            data.append(([temp, humidity, nutrients, ph], [growth, branching]))
        return data

    def training_pairs(name: str, data: Any, samples: int) -> list:
        if isinstance(data, str):
            if data == "growth_pattern":
                return growth_pattern(samples)
            raise MyceliumRuntimeError(f"{name}(): unknown training pattern \"{data}\" (use \"growth_pattern\")")
        pairs = []
        for item in _need_list(name, data, "training data: an array of [inputs, targets] pairs"):
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise MyceliumRuntimeError(f"{name}(): each training item must be an [inputs, targets] pair")
            pairs.append((list(item[0]), list(item[1])))
        return pairs

    @define("create_bio_network",
            "create_bio_network(id, input_size=4, hidden_size=8, output_size=2) a growing neural network")
    def _create_bio_network(network_id: Any, input_size: Any = 4, hidden_size: Any = 8, output_size: Any = 2) -> str:
        network_id = _need_string("create_bio_network", network_id, "a network id")
        sizes = [_need_int("create_bio_network", v) for v in (input_size, hidden_size, output_size)]
        interp.bio_ml.create_network(network_id, *sizes)
        return f"Created bio-network '{network_id}' with architecture {sizes[0]}-{sizes[1]}-{sizes[2]}"

    @define("train_bio_network", "train_bio_network(id, data, epochs=50) data is \"growth_pattern\" or pairs")
    def _train_bio_network(network_id: Any, training_data: Any, epochs: Any = 50) -> dict:
        network_id = _need_string("train_bio_network", network_id, "a network id")
        pairs = training_pairs("train_bio_network", training_data, 20)
        result = interp.bio_ml.train_network(network_id, pairs, _need_int("train_bio_network", epochs))
        return {"fitness": result["final_fitness"], "time": result["training_time"], "cycles": result["growth_cycles"]}

    @define("predict_bio_network", "predict_bio_network(id, inputs) run the network forward")
    def _predict_bio_network(network_id: Any, inputs: Any) -> list:
        network_id = _need_string("predict_bio_network", network_id, "a network id")
        return interp.bio_ml.predict(network_id, _need_list("predict_bio_network", inputs, "an inputs array"))

    @define("compare_bio_ml", "compare_bio_ml(data=\"growth_pattern\") train small, medium and large networks")
    def _compare_bio_ml(training_data: Any = "growth_pattern") -> dict:
        pairs = training_pairs("compare_bio_ml", training_data, 30)
        results = interp.bio_ml.compare_biological_approaches(pairs)
        return {name: {"fitness": r["final_fitness"], "time": r["training_time"]} for name, r in results.items()}

    def controller(name: str, cultivation_id: Any):
        cultivation_id = _need_string(name, cultivation_id, "a cultivation id")
        if cultivation_id not in interp.cultivation.cultivations:
            raise MyceliumRuntimeError(f"{name}(): cultivation \"{cultivation_id}\" not found")
        return interp.cultivation.cultivations[cultivation_id]

    @define("create_cultivation", "create_cultivation(id) a simulated cultivation with sensors and a growth model")
    def _create_cultivation(cultivation_id: Any) -> str:
        cultivation_id = _need_string("create_cultivation", cultivation_id, "a cultivation id")
        if cultivation_id in interp.cultivation.cultivations:
            raise MyceliumRuntimeError(f"create_cultivation(): cultivation \"{cultivation_id}\" already exists")
        interp.cultivation.create_cultivation(cultivation_id)
        return f"Created cultivation system '{cultivation_id}'"

    @define("monitor_cultivation", "monitor_cultivation(id) current simulated reading")
    def _monitor_cultivation(cultivation_id: Any) -> dict:
        ctl = controller("monitor_cultivation", cultivation_id)
        reading = ctl.get_current_reading()
        alerts = ctl.check_alerts(reading)
        return {
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "growth_rate": reading.growth_rate,
            "alerts": len(alerts),
            "stage": ctl.stage.value,
        }

    @define("get_cultivation_health", "get_cultivation_health(id) health score from the growth model")
    def _get_cultivation_health(cultivation_id: Any) -> dict:
        ctl = controller("get_cultivation_health", cultivation_id)
        health = ctl.analyze_cultivation_health(ctl.get_current_reading())
        return {
            "health_score": health["health_score"],
            "predicted_growth": health.get("predicted_growth", 0.0),
            "recommendations": len(health.get("recommendations", []) or []),
        }

    @define("optimize_cultivation", "optimize_cultivation(id) genetic search over temperature, humidity, nutrients")
    def _optimize_cultivation(cultivation_id: Any) -> dict:
        ctl = controller("optimize_cultivation", cultivation_id)

        def fitness(params: List[float]) -> float:
            temp, humidity, nutrients = params
            temp_factor = max(0.0, 1.0 - abs(temp - 24.0) / 8.0)
            humidity_factor = max(0.0, min(1.0, humidity / 100.0))
            nutrient_factor = max(0.0, min(1.0, nutrients / 120.0))
            return temp_factor * humidity_factor * nutrient_factor

        result = ctl.bio_optimizer.optimize("genetic", fitness, 3, population_size=20, max_generations=20)
        solution = result["best_solution"]
        return {
            "fitness": result["best_fitness"],
            "optimal_temperature": solution[0],
            "optimal_humidity": solution[1],
            "optimal_nutrients": solution[2],
            "time": result["computation_time"],
        }
