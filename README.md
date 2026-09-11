# Mycelium-EI-Lang

Mycelium-EI-Lang is a small interpreted language for cultivation models: environment parameters, adapt functions that fire when they change, and genetic, particle swarm and ant colony optimizers.

## Status

early stage

0.2.0 is the first version whose `pip install` runs `.myc` programs. Releases 0.1.0 to 0.1.2 installed an interpreter that parsed Python syntax and imported a dependency they did not declare, so `myc examples/hello_world.myc` failed on every clean install.

What does not work yet:

- One file per program. There is no `import`, no module system and no standard library beyond the builtins listed in `docs/reference.md`.
- The interpreter walks the syntax tree in Python. Loops of a few hundred thousand iterations take seconds.
- The optimizers, the neural network and the cultivation monitor are demonstration models: small populations, a Hebbian toy network, readings drawn from `random.gauss`. None of it reads a sensor or controls equipment.
- The Rust crate under `compiler/` builds and passes its two tests, but it is a skeleton with no command-line tool. The Python package does not use it. Nothing here compiles to native code or WebAssembly.
- Run only on macOS (arm64). Linux and Windows have not been tried.

## Install and first run

Run on 2026-09-11 with CPython 3.13.14 on macOS.

```
python3 -m venv .venv
. .venv/bin/activate
pip install mycelium-ei-lang
myc --version
```

Output:

```
mycelium-ei-lang 0.2.0
```

Save this as `hello.myc`:

```
// Hello World in Mycelium-EI-Lang

environment {
    temperature: 22.5,
    humidity: 85.0
}

function main() {
    print("Hello from the Mycelium Network!")

    let greeting: string = "Welcome to ecological intelligence programming"
    print(greeting)

    let temp: float = get_env("temperature")
    if temp > 20.0 {
        print("Optimal growth conditions detected")
    } else {
        print("Adjusting environmental parameters...")
    }
}
```

Then run it:

```
myc hello.myc
```

Output:

```
Hello from the Mycelium Network!
Welcome to ecological intelligence programming
Optimal growth conditions detected
```

`mycelium` and `python -m mycelium_ei` are the same command as `myc`. The package has no dependencies. The twelve programs in `examples/` and the tests are in the repository: `git clone https://github.com/MichaelCrowe11/mycelium-ei-lang`, then `pip install -e . pytest` and `pytest` in the checkout.

## What runs today

Each item is covered by a test in `tests/`; the suite (140 tests) passed on CPython 3.9, 3.10, 3.11, 3.12, 3.13 and 3.14 on macOS on 2026-09-11.

- The language in `docs/reference.md`: `environment` blocks, functions, `let` and `const`, `if`/`else if`/`else`, `while`, `for` over arrays, objects, strings and ints, arrays and objects with methods, string concatenation, `mycelium` declarations with fields, methods, `init` and `adapt` functions, `new`, and top-level `network` and `signal` declarations (`tests/test_interpreter.py`, `tests/test_parser.py`, `tests/test_lexer.py`).
- `adapt` functions run when `set_env` or `update_global_env` changes a parameter; `examples/cultivation.myc` and `examples/neural_network.myc` show it (`tests/test_examples.py`).
- All twelve programs in `examples/` run to completion under `myc --no-sleep --seed 1` (`tests/test_examples.py`).
- `genetic_optimize`, `swarm_optimize`, `ant_optimize` and `bio_compare` in pure Python; a fitness function takes one array or one argument per dimension (`tests/test_bio.py`, `examples/bio_optimization_demo.myc`).
- Network builtins: nodes, connections, broadcast signals that print as they arrive (`examples/network_demo.myc`).
- Toy neural network and simulated cultivation builtins (`examples/bio_ml_demo.myc`, `examples/cultivation_platform_demo.myc`).
- Command line: `--check`, `--tokens`, `--ast`, `--no-sleep`, `--seed`, `-` for standard input; errors print as `file:line:column: runtime error: ...` and exit 1; runaway recursion stops with a message instead of a crash (`tests/test_cli.py`).
- Importing the package pulls in no third-party module (`tests/test_no_dependencies.py`).
- `cargo build` and `cargo test` pass for `compiler/` (one unit test, one doc test).

## Limits

- This is an interpreter for small models, not a numerical library. The optimizers search `[-1, 1]` per dimension with populations of tens; no speed or quality claim is made against established packages.
- `create_cultivation` and `monitor_cultivation` simulate a grow room. Do not use them to run one.
- `quantum_bio_computing.py` and `performance_optimizations.py` at the repository root are standalone experiments from 2025 that need numpy and numba. They are not part of the package and have no tests.
- The directories `crypto-payments/`, `npm-package/`, `vscode-extension/`, `wasm/`, `snap/`, `homebrew/`, `conda-recipe/` and the two Dockerfiles have not been run. The planning documents at the root (roadmaps, monetization, publishing) describe 2025 intentions and prices. They are not an offer.
- Syntax errors are reported one at a time, at the first token the parser cannot place.

## License and contact

Proprietary. See `LICENSE`: viewing and personal non-commercial evaluation only; no copying, modification or redistribution.

Contact: michael@crowelogic.com
