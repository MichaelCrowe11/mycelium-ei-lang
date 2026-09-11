# Mycelium-EI-Lang reference

This is the whole language as the interpreter in `mycelium_ei` runs it. Every
construct here is exercised by `tests/` or by a program in `examples/`.

## Running programs

```
myc program.myc            run a program (main() runs last if it is defined)
myc --check program.myc    parse only, report syntax errors
myc --tokens program.myc   print the token stream
myc --ast program.myc      print the syntax tree
myc --no-sleep ...         sleep() returns at once (also MYCELIUM_NO_SLEEP=1)
myc --seed 1 ...           seed the random number generator for repeatable runs
myc -                      read the program from standard input
```

`mycelium` and `python -m mycelium_ei` are the same command. Exit code 0 means
the program ran to the end, 1 means a syntax or runtime error (printed to
standard error as `file:line:column: kind: message`), 2 means no file was given.

From Python:

```python
from mycelium_ei import run_file, run_source, Interpreter

run_file("examples/hello_world.myc")
lines = []
interp = Interpreter("<inline>", write=lines.append, no_sleep=True, seed=1)
interp.run('print("hi", 1 + 1)')
assert lines == ["hi 2"]
```

## Lexical rules

- Comments: `// to end of line` and `/* block */`.
- Integers `42`, floats `1.5`, `2e-3`; strings in double quotes with the
  escapes `\n \t \r \" \\ \0`; `true`, `false`, `null`.
- Identifiers: letters, digits and `_`, not starting with a digit.
- Keywords: `environment function mycelium network signal adapt if else while
  for in return let const new true false null`. Keywords may be used as
  object keys and after `.` (`stats.environment`).
- Statements end at the end of the expression; `;` is allowed and ignored.
  A call or index must start on the same line as the expression it applies
  to, so a line that starts with `(` or `[` begins a new statement.

## Types and values

`int`, `float`, `string`, `bool`, `null`, `array` (`[1, 2]`), `object`
(`{key: value, "other key": 2}`), `function`, and instances of `mycelium`
declarations. `type_of(x)` returns the name. Type annotations (`let x: float`,
`function f(a: int) -> float`) are accepted and ignored.

Truthiness follows Python: `0`, `0.0`, `""`, `[]`, `{}` and `null` are false.

`print` shows booleans as `true`/`false`, `null` as `null`, floats with full
precision, and quotes strings inside arrays and objects.

## Expressions

Precedence, lowest first: assignment `=`; `||`; `&&`; `==` `!=`; `<` `>` `<=`
`>=`; `+` `-`; `*` `/` `%`; unary `!` `-`; postfix call `f(x)`, index `a[i]`,
property `a.b`; primary.

- `+` on a string and anything concatenates (the other operand is formatted
  as `print` would show it); on two arrays it concatenates them.
- `/` always gives a float; `%` follows Python. Division or modulo by zero is
  a runtime error.
- `<` and friends compare numbers with numbers or strings with strings.
- `&&` and `||` short-circuit and return the deciding operand.
- Indexing an array out of range is an error; `object["missing"]` is an error;
  `object.missing` is `null`.
- Assignment targets: a variable declared with `let`, `array[i]`,
  `object.key`, `object[key]`, `instance.field`.

## Statements

```
let x: float = 1.0          // declare; type is optional and ignored
const limit = 10            // assigning to a const is an error
x = x + 1                   // assignment needs a prior let
if a < b { ... } else if a == b { ... } else { ... }
while cond { ... }
for item in [1, 2, 3] { ... }     // arrays: items; objects: keys; strings: characters
for i in 5 { ... }                // an int iterates 0..4; range(a, b) builds an array
return expr                       // bare return at end of line returns null
```

Blocks open a new scope: a `let` inside `if`, `while`, `for` or a function is
not visible outside it. Assignment finds the nearest enclosing declaration.

## Functions

```
function name(a, b: float) -> float {
    return a * b
}
```

Calls must pass exactly as many arguments as there are parameters. Functions
are values: `let f = name`. A user function with the same name as a builtin
replaces it. If `main` is defined it runs after all top-level statements.

Runaway recursion stops with `Maximum call depth (N) exceeded`. N is 2000 for
the `myc` command, which runs the program on a thread with a 256 MB stack, and
200 for `Interpreter` used directly from Python (`max_call_depth=` changes it;
on CPython 3.10 and older, going higher needs `run_in_thread`).

## Environment block and adapt functions

```
environment {
    temperature: 22.5,
    humidity: 85.0
}

adapt function respond() {
    if get_env("temperature") > 28.0 { print("too warm") }
}

set_env("temperature", 30.0)     // prints "too warm"
```

`get_env(name)` reads a declared parameter (an undeclared name is an error);
`set_env(name, value)` and `update_global_env(name, value)` set one and then
run every `adapt` function once: top-level `adapt function`s with no
parameters, then the `adapt function` methods of every live `mycelium`
instance. An adapt function that itself calls `set_env` does not restart the
pass. `env()` returns all parameters as an object.

## mycelium, network and signal declarations

```
network Substrate { nodes: 4, density: 0.75 }      // a named record (an object)
signal Pulse { amplitude: float, speed: float }     // a record type

mycelium Colony {
    signal growth: float = 1.0        // field with a default
    signal label: string              // field with a typed zero value ("")
    network links: Substrate          // field: a copy of the Substrate record
    network local { size: 2 }         // field: an inline record
    signal pulse: Pulse               // field: {amplitude: 0.0, speed: 0.0}

    function init(name) { label = name }          // optional; receives the new arguments
    function grow(by) { growth = growth + by; return describe() }
    function describe() { return label + ": " + growth }
    adapt function react() { growth = growth * 2.0 }
}

let c = new Colony("alpha")
c.grow(0.5)            // method call
c.growth               // field read
c.links.nodes = 8      // fields are ordinary values
```

Inside a method, fields and the other methods are reachable by bare name and
assignment to a field name updates the instance. Zero values by type: `float`
0.0, `int` 0, `string` "", `bool` false, `array` [], `object` {}, anything
else `null`. Each instance gets its own copy of record-typed fields.

## Methods on arrays, strings and objects

Arrays: `append(x...)` (alias `push`), `pop([i])`, `insert(i, x)`,
`remove(x)`, `contains(x)`, `index_of(x)` (-1 if absent), `sort()`,
`reverse()`, `join(sep)`, `slice(start[, end])`, `copy()`, `length`.

Strings: `upper()`, `lower()`, `trim()`, `split([sep])`, `contains(s)`,
`starts_with(s)`, `ends_with(s)`, `replace(old, new)`, `index_of(s)`,
`length`. Strings are indexable: `s[0]`.

Objects: `keys()`, `values()`, `has(key)`, `remove(key)`, `copy()`, `length`.
A key that is also a method name is returned as the key's value.

## Builtin functions

Output and collections: `print(values...)`, `len(x)`, `range(end)` /
`range(start, end[, step])`, `reverse(array)`, `sorted(array)`,
`sum(array)`, `keys(obj)`, `values(obj)`, `has(obj, key)`,
`contains(array_or_string, item)`, `join(array[, sep])`, `split(string[, sep])`.

Math: `abs`, `min(a, b, ...)` or `min(array)`, `max`, `sqrt`, `pow(x, y)`,
`exp`, `log(x[, base])`, `sin`, `cos`, `tan`, `floor`, `ceil`,
`round(x[, digits])`, `random()` in [0, 1), `random_range(low, high)`,
`random_int(low, high)`, `clock()` (seconds, monotonic).

Conversion: `int`, `float`, `str`, `bool`, `type_of`.

Environment: `get_env`, `set_env`, `env`, `sleep(milliseconds)`.

Cultivation helpers: `calculate_growth_factor(temp, humidity, co2)` (a 0..1
factor centred on 24 C, 85 percent humidity and 1000 ppm CO2),
`create_one_hot(index, size)`, `apply_activation(x, "relu" | "sigmoid" |
"tanh" | "linear")` or `apply_activation(array, "softmax")`,
`apply_signal_decay(x_or_array, distance)` (multiplies by `exp(-0.1 *
distance)`), `signal_alert(message)` and `signal_network(type, value)` (both
print one line).

Network: `create_network([name])`, `add_node([network])` (connects the new
node to the previous one; ids are `node_01`, `node_02`, ...),
`connect_nodes(a, b)`, `broadcast_signal(type, payload[, network])` with type
`growth`, `nutrient`, `stress`, `alert` or `data`, `update_global_env(name,
value[, network])`, `get_network_stats([network])` returning `{name, nodes,
connections, environment}`. Nodes print a line when they receive a signal.

Optimizers (pure Python, maximise the fitness, search space [-1, 1] per
dimension): `genetic_optimize(fitness, dimensions=6, population_size=50,
max_generations=100)`, `swarm_optimize(fitness, dimensions=6,
num_particles=30, max_iterations=100)`, `ant_optimize(fitness, dimensions=6,
num_ants=25, max_iterations=100)`, `bio_compare(fitness, dimensions=6)`. The
fitness is a function or a function name; it takes either one array or one
parameter per dimension and must return a number. Results are objects with
`solution`, `fitness`, `time` and `generations` or `iterations`; `bio_compare`
returns `{genetic: {...}, pso: {...}, aco: {...}}`. The optimizers print
progress lines.

Toy neural network (Hebbian-style adaptation, no gradient descent):
`create_bio_network(id, input_size=4, hidden_size=8, output_size=2)`,
`train_bio_network(id, data, epochs=50)` where data is `"growth_pattern"`
(20 generated samples) or an array of `[inputs, targets]` pairs,
`predict_bio_network(id, inputs)`, `compare_bio_ml([data])`.

Simulated cultivation (readings come from `random.gauss`, not sensors):
`create_cultivation(id)`, `monitor_cultivation(id)` returning `{temperature,
humidity, growth_rate, alerts, stage}`, `get_cultivation_health(id)` returning
`{health_score, predicted_growth, recommendations}`,
`optimize_cultivation(id)` returning `{fitness, optimal_temperature,
optimal_humidity, optimal_nutrients, time}`.

## Errors

Syntax errors stop before anything runs. Runtime errors stop the program at
the failing line. Both print as `file:line:column: syntax error: ...` or
`file:line:column: runtime error: ...`. From Python they are
`mycelium_ei.MyceliumSyntaxError` and `mycelium_ei.MyceliumRuntimeError`
(both `MyceliumError`) with `line`, `column`, `filename` and `format()`.
