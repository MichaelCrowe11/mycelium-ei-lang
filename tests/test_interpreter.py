import time

import pytest

from mycelium_ei.errors import MyceliumRuntimeError


def test_arithmetic_and_precedence(run):
    assert run("print(1 + 2 * 3, 7 / 2, 7 % 3, -(2 + 3), 2 * (3 + 4))") == ["7 3.5 1 -5 14"]


def test_string_concatenation_formats_values(run):
    assert run('print("a" + 1 + true + null + 2.5)') == ["a1truenull2.5"]


def test_print_formatting(run):
    assert run('print(true, false, null, [1, "two", [3]], {a: 1, "b c": "x"})') == [
        'true false null [1, "two", [3]] {a: 1, "b c": "x"}']


def test_comparisons(run):
    assert run("print(1 < 2, 2 <= 2, 3 > 4, 1 == 1.0, \"a\" != \"b\", \"a\" < \"b\")") == [
        "true true false true true true"]


def test_logical_operators_short_circuit_and_return_operands(run):
    assert run("print(false && undefined_function(), true || undefined_function(), 0 || 5, 2 && 3)") == [
        "false true 5 3"]


def test_truthiness(run):
    src = 'if 0 { print("yes") } else { print("zero is false") }\nif "" { } else { print("empty string is false") }\nif [] { } else { print("empty array is false") }'
    assert run(src) == ["zero is false", "empty string is false", "empty array is false"]


def test_let_const_and_reassignment(run):
    assert run("let a = 1\na = a + 1\nprint(a)") == ["2"]
    with pytest.raises(MyceliumRuntimeError, match="Cannot assign to constant 'c'"):
        run("const c = 1\nc = 2")


def test_assignment_to_undefined_variable_is_an_error(run):
    with pytest.raises(MyceliumRuntimeError, match="declare it first with 'let'"):
        run("x = 1")


def test_undefined_variable_error_mentions_line(run):
    with pytest.raises(MyceliumRuntimeError) as info:
        run("let a = 1\nprint(b)")
    assert "Undefined variable 'b'" in str(info.value)
    assert info.value.line == 2


def test_environment_parameter_hint(run):
    with pytest.raises(MyceliumRuntimeError, match='use get_env\\("temperature"\\)'):
        run("environment { temperature: 22.0 }\nprint(temperature)")


def test_block_scoping(run):
    with pytest.raises(MyceliumRuntimeError, match="Undefined variable 'inner'"):
        run("if true { let inner = 1 }\nprint(inner)")
    assert run("let outer = 1\nif true { outer = 2 }\nprint(outer)") == ["2"]


def test_for_loops_over_arrays_objects_strings_ints_and_ranges(run):
    src = """
    for x in [1, 2] { print(x) }
    for k in {a: 1, b: 2} { print(k) }
    for ch in "hi" { print(ch) }
    for i in 2 { print(i) }
    for j in range(3, 5) { print(j) }
    """
    assert run(src) == ["1", "2", "a", "b", "h", "i", "0", "1", "3", "4"]


def test_for_over_null_is_an_error(run):
    with pytest.raises(MyceliumRuntimeError, match="Cannot iterate over null"):
        run("for x in null { }")


def test_while_loop(run):
    assert run("let i = 0\nwhile i < 3 { i = i + 1 }\nprint(i)") == ["3"]


def test_functions_and_recursion(run):
    src = """
    function fib(n) {
        if n < 2 { return n }
        return fib(n - 1) + fib(n - 2)
    }
    print(fib(10))
    """
    assert run(src) == ["55"]


def test_return_inside_nested_loops(run):
    src = """
    function find(target) {
        for i in range(0, 5) {
            for j in range(0, 5) {
                if i * j == target { return [i, j] }
            }
        }
        return null
    }
    print(find(6), find(99))
    """
    assert run(src) == ["[2, 3] null"]


def test_function_without_return_gives_null(run):
    assert run("function f() { }\nprint(f())") == ["null"]


def test_arity_mismatch(run):
    with pytest.raises(MyceliumRuntimeError, match="Function 'f' expects 2 argument\\(s\\), got 1"):
        run("function f(a, b) { }\nf(1)")


def test_undefined_function(run):
    with pytest.raises(MyceliumRuntimeError, match="Undefined function 'nope'"):
        run("nope()")


def test_functions_are_values(run):
    assert run("function double(x) { return x * 2 }\nlet f = double\nprint(f(4), type_of(f))") == ["8 function"]


def test_user_functions_shadow_builtins(run):
    assert run("function abs(x) { return 99 }\nprint(abs(-1))") == ["99"]


def test_main_runs_after_top_level_statements(run):
    assert run('print("top")\nfunction main() { print("main") }') == ["top", "main"]


def test_arrays(run):
    src = """
    let a = [1, 2, 3]
    a.append(4)
    a[0] = 10
    print(a, a[-1], a.length, len(a), a.contains(2), a.index_of(3))
    let last = a.pop()
    print(last, a, a.slice(1), reverse(a), sorted([3, 1, 2]), [1] + [2])
    """
    assert run(src) == ["[10, 2, 3, 4] 4 4 4 true 2", "4 [10, 2, 3] [2, 3] [3, 2, 10] [1, 2, 3] [1, 2]"]


def test_array_index_out_of_range(run):
    with pytest.raises(MyceliumRuntimeError, match="Index 3 out of range for array of length 3"):
        run("let a = [1, 2, 3]\nprint(a[3])")


def test_objects(run):
    src = """
    let o = {a: 1, "b": 2}
    o.c = 3
    o["d"] = 4
    print(o.a, o["b"], o.missing, o.keys(), o.has("c"), len(o))
    """
    assert run(src) == ["1 2 null [\"a\", \"b\", \"c\", \"d\"] true 4"]


def test_object_missing_key_via_index_is_an_error(run):
    with pytest.raises(MyceliumRuntimeError, match='Key "zz" not found in object'):
        run('let o = {a: 1}\nprint(o["zz"])')


def test_strings(run):
    src = 'let s = "Hello World"\nprint(s.length, s.upper(), s.split(" "), s.contains("World"), s[0], join(["a", "b"], "-"))'
    assert run(src) == ['11 HELLO WORLD ["Hello", "World"] true H a-b']


def test_environment_block_and_get_set_env(run):
    src = """
    environment { temperature: 22.5, humidity: 85.0 }
    print(get_env("temperature"))
    set_env("temperature", 26.0)
    print(get_env("temperature"), env())
    """
    assert run(src) == ["22.5", "26.0 {temperature: 26.0, humidity: 85.0}"]


def test_unknown_environment_parameter(run):
    with pytest.raises(MyceliumRuntimeError, match="Unknown environment parameter 'ph'"):
        run('print(get_env("ph"))')


def test_top_level_adapt_function_fires_on_set_env(run):
    src = """
    environment { temperature: 22.0 }
    adapt function respond() { print("adapting to", get_env("temperature")) }
    set_env("temperature", 30.0)
    print("done")
    """
    assert run(src) == ["adapting to 30.0", "done"]


def test_adapt_function_does_not_retrigger_itself(run):
    src = """
    environment { temperature: 22.0 }
    adapt function respond() {
        print("adapt")
        set_env("temperature", get_env("temperature") + 1.0)
    }
    set_env("temperature", 30.0)
    print(get_env("temperature"))
    """
    assert run(src) == ["adapt", "31.0"]


MYCELIUM_SRC = """
environment { temperature: 24.0 }

network Topology { nodes: 4, density: 0.5 }
signal Pulse { amplitude: float, speed: float }

mycelium Colony {
    signal growth: float = 1.0
    signal label: string
    network links: Topology
    network local { size: 2 }
    signal pulse: Pulse

    function grow(by) {
        growth = growth + by
        return describe()
    }

    function describe() -> string {
        return "growth " + growth
    }

    adapt function react() {
        growth = growth * 2.0
        pulse.speed = get_env("temperature") / 10.0
    }
}
"""


def test_mycelium_instances_fields_and_methods(interp_run):
    src = MYCELIUM_SRC + """
    function main() {
        let c = new Colony()
        print(c.growth, c.label, c.links, c.local.size, c.pulse)
        print(c.grow(0.5))
        c.links.nodes = 99
        let d = new Colony()
        print(d.links.nodes, c.links.nodes)
        print(type_of(c), c)
    }
    """
    interp, lines = interp_run(src)
    assert lines == [
        "1.0  {nodes: 4, density: 0.5} 2 {amplitude: 0.0, speed: 0.0}",
        "growth 1.5",
        "4 99",
        'Colony Colony {growth: 1.5, label: "", links: {nodes: 99, density: 0.5}, local: {size: 2}, pulse: {amplitude: 0.0, speed: 0.0}}',
    ]


def test_mycelium_adapt_methods_fire_on_set_env(run):
    src = MYCELIUM_SRC + """
    function main() {
        let c = new Colony()
        set_env("temperature", 30.0)
        print(c.growth, c.pulse.speed)
    }
    """
    assert run(src) == ["2.0 3.0"]


def test_mycelium_init_receives_new_arguments(run):
    src = """
    mycelium Batch {
        signal name: string
        function init(n) { name = n }
    }
    let b = new Batch("alpha")
    print(b.name)
    """
    assert run(src) == ["alpha"]


def test_new_without_init_rejects_arguments(run):
    with pytest.raises(MyceliumRuntimeError, match="has no 'init' function"):
        run("mycelium B { signal x: int }\nlet b = new B(1)")


def test_unknown_mycelium(run):
    with pytest.raises(MyceliumRuntimeError, match="Unknown mycelium 'Nope'"):
        run("let x = new Nope()")


def test_unknown_field_is_an_error(run):
    with pytest.raises(MyceliumRuntimeError, match="Mycelium 'B' has no field or function 'zz'"):
        run("mycelium B { signal x: int }\nlet b = new B()\nprint(b.zz)")


def test_builtin_math(run):
    src = """
    print(abs(-2), min(3, 1, 2), max([4, 9, 2]), sqrt(16), pow(2, 10), round(2.567, 2), round(2.5), floor(2.7), ceil(2.1))
    print(sum([1, 2, 3.5]), int("42"), float("1.5"), str(12), int(3.9), type_of(1), type_of(1.0), type_of("s"), type_of([]), type_of({}), type_of(null))
    """
    assert run(src) == [
        "2 1 9 4.0 1024.0 2.57 2 2 3",
        "6.5 42 1.5 12 3 int float string array object null",
    ]


def test_builtin_errors_have_clear_messages(run):
    with pytest.raises(MyceliumRuntimeError, match="sqrt\\(\\) needs a non-negative number, got -1"):
        run("sqrt(-1)")
    with pytest.raises(MyceliumRuntimeError, match="range\\(\\) needs an int, got string"):
        run('range("a")')
    with pytest.raises(MyceliumRuntimeError, match="Division by zero"):
        run("print(1 / 0)")
    with pytest.raises(MyceliumRuntimeError, match="Cannot apply '-' to string and int"):
        run('print("a" - 1)')
    with pytest.raises(MyceliumRuntimeError, match="Cannot compare string and int"):
        run('print("a" < 1)')


def test_mycelium_specific_builtins(run):
    src = """
    print(calculate_growth_factor(24.0, 85.0, 1000.0), calculate_growth_factor(14.0, 85.0, 1000.0))
    print(create_one_hot(1, 3), apply_activation(-2.0, "relu"), apply_activation(0.0, "sigmoid"), round(sum(apply_activation([1.0, 2.0, 3.0], "softmax")), 6))
    print(apply_signal_decay(1.0, 0.0), apply_signal_decay([2.0], 0.0))
    signal_alert("low nutrients")
    signal_network("stress", true)
    """
    assert run(src) == [
        "1.0 0.0",
        "[0.0, 1.0, 0.0] 0.0 0.5 1.0",
        "1.0 [2.0]",
        "ALERT: low nutrients",
        "Network signal: stress = true",
    ]


def test_network_builtins(run, capsys):
    src = """
    let a = add_node()
    let b = add_node()
    let stats = get_network_stats()
    print(stats.nodes, stats.connections, a.node_id, b.node_id)
    broadcast_signal("growth", {rate: 0.8})
    """
    lines = run(src)
    assert lines == ["2 1 node_01 node_02"]
    captured = capsys.readouterr().out
    assert "Connected node_01 <-> node_02" in captured
    assert "Node node_02: Received growth signal" in captured


def test_sleep_is_skipped_when_disabled(run):
    started = time.time()
    run("sleep(5000)")
    assert time.time() - started < 1.0


def test_sleep_argument_validation(run):
    with pytest.raises(MyceliumRuntimeError, match="non-negative number of milliseconds"):
        run("sleep(-1)")


def test_deep_recursion_is_reported_not_crashed(run):
    with pytest.raises(MyceliumRuntimeError, match="Maximum call depth \\(200\\) exceeded in function 'f'"):
        run("function f(n) { return f(n + 1) }\nf(0)")


def test_recursion_within_the_cap_works(run):
    src = "function count(n) { if n == 0 { return 0 } return 1 + count(n - 1) }\nprint(count(180))"
    assert run(src) == ["180"]


def test_call_depth_cap_is_configurable(run):
    with pytest.raises(MyceliumRuntimeError, match="Maximum call depth \\(20\\)"):
        run("function f(n) { return f(n + 1) }\nf(0)", max_call_depth=20)


def test_runtime_error_inside_function_points_at_the_line(run):
    with pytest.raises(MyceliumRuntimeError) as info:
        run("function f() {\n  let a = 1\n  return a / 0\n}\nf()")
    assert info.value.line == 3


def test_seed_makes_random_repeatable(run):
    first = run("print(random(), random_int(1, 100))", seed=7)
    second = run("print(random(), random_int(1, 100))", seed=7)
    assert first == second


def test_run_in_thread_allows_deeper_recursion():
    from mycelium_ei.interpreter import Interpreter, run_in_thread
    lines = []
    interp = Interpreter("<t>", write=lines.append, no_sleep=True, max_call_depth=2000)
    src = "function count(n) { if n == 0 { return 0 } return 1 + count(n - 1) }\nprint(count(1500))"
    run_in_thread(lambda: interp.run(src))
    assert lines == ["1500"]


def test_run_in_thread_propagates_errors():
    from mycelium_ei.interpreter import Interpreter, run_in_thread
    interp = Interpreter("<t>", write=lambda s: None, no_sleep=True, max_call_depth=2000)
    with pytest.raises(MyceliumRuntimeError, match="Maximum call depth \\(2000\\)"):
        run_in_thread(lambda: interp.run("function f(n) { return f(n + 1) }\nf(0)"))
