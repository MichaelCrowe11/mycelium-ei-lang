# Changelog

## Unreleased

### Removed

- The 2025 planning documents and never-run directories at the repository
  root: `crypto-payments/`, `npm-package/`, `vscode-extension/`, `wasm/`,
  `snap/`, `homebrew/`, `conda-recipe/`, `marketing/`, both Dockerfiles, the
  roadmap, monetization, publishing and demo documents, and the two root
  experiments `quantum_bio_computing.py` and `performance_optimizations.py`.
  All of GitHub's 77 Dependabot alerts came from lockfiles in those
  directories. The files stay in the history and on the `archive/2025-planning`
  branch. No packaged code changed.

## 0.2.2 (2026-09-11)

First release on PyPI, published as `mycelium-ei-language`.

### Changed

- The distribution is renamed from `mycelium-ei-lang` to `mycelium-ei-language`.
  The PyPI project `mycelium-ei-lang` belongs to an account whose two-factor
  device and email were lost with a laptop, so it cannot receive releases and
  its 0.1.x uploads stay broken. The import name `mycelium_ei`, the `myc` and
  `mycelium` commands and the repository name are unchanged. `myc --version`
  prints the distribution name: `mycelium-ei-language 0.2.2`.

## 0.2.1 (2026-09-11)

The license fix release, and the first version uploaded to PyPI. 0.2.0 was
published only as a GitHub release (tag v0.2.0) while the PyPI upload waited
on an account permission; it never reached PyPI.

### Fixed

- Every surface now says proprietary. `compiler/Cargo.toml` claimed
  Apache-2.0 and `vscode-extension/package.json` claimed MIT; both point at
  the one `LICENSE` now. Two marketing drafts called the language open
  source and the Solidity template header said MIT.
- `LICENSE` had a placeholder contact (`michael.benjamin.crowe@[domain]`) and
  a support address on a domain that does not resolve. It now gives
  michael@crowelogic.com and the GitHub issue tracker, and the copyright
  year covers 2024-2026.

## 0.2.0 (2026-09-11)

The first release whose `pip install` runs the documented language.

### Fixed

- Releases 0.1.0 to 0.1.2 shipped a `mycelium_ei` module that parsed input with
  Python's `ast` module, so every `.myc` program failed with `invalid syntax`,
  and they declared no dependencies while importing numpy, so `import mycelium_ei`
  failed on a clean install. 0.2.0 ships a lexer, parser and tree-walking
  interpreter for the `.myc` grammar and has no runtime dependencies.
- `examples/cultivation.myc` called `adapt_environment()`, which did not exist.
  It now calls the `adjust_to_environment()` adapt function it defines.
- `examples/neural_network.myc` called four functions that existed nowhere
  (`create_signal`, `ecological_loss`, `update_mycelial_connections`,
  `adapt_to_environment`). It is rewritten as a complete, smaller program that
  uses the same constructs: a `network` record, a `signal` type, a `mycelium`
  with methods and an `adapt function`, `new`, method calls and array methods.
- Version strings agreed nowhere (pyproject 0.1.0, package 0.1.1, PyPI 0.1.2).
  The version now lives only in `mycelium_ei/__init__.py`; `setup.py` is gone.
- The Rust workspace listed members that were not in the repository, so
  `cargo` could not start. The workspace now lists only `compiler`, which
  builds and passes its one test after a logos 0.13 migration and a borrow fix.
  It is still a library skeleton and the Python package does not use it.

### Added

- Language: `else if` chains, `null`, `const` (assignment is an error), object
  literals `{key: value}` with identifier or string keys, indexing `a[i]`,
  property access `a.b` and assignment to indexed and property targets,
  method calls on arrays (`append`, `pop`, `insert`, `remove`, `contains`,
  `index_of`, `sort`, `reverse`, `join`, `slice`, `copy`, `length`), strings
  (`upper`, `lower`, `trim`, `split`, `contains`, `starts_with`, `ends_with`,
  `replace`, `index_of`, `length`) and objects (`keys`, `values`, `has`,
  `remove`, `copy`, `length`), block comments `/* */`, string escapes,
  exponent literals, `for` over arrays, objects, strings and ints.
- `mycelium` blocks are classes: `signal` fields with defaults or types,
  inline or typed `network` fields, methods, an optional `init` method that
  receives the `new` arguments, and `adapt function` methods. Inside a method
  the fields and the other methods are reachable by bare name.
- Top-level `network Name { ... }` declares a named record and `signal Name
  { field: type }` declares a record type; a typed field gets a copy of the
  record or a zero-filled instance.
- `adapt` functions run once each time `set_env` or `update_global_env`
  changes a parameter; an adapt function that itself calls `set_env` does not
  retrigger the pass.
- Error messages carry `file:line:column`, and the `myc` command prints them
  as `runtime error:` or `syntax error:` lines and exits 1.
- Runaway recursion is reported as `Maximum call depth (N) exceeded` instead
  of crashing the process. The cap is 200 nested calls from Python and 2000
  from the `myc` command, which runs the program on a thread with a 256 MB
  stack (CPython 3.10 and older overflow the main thread's stack far earlier).
- `print` shows `true`, `false` and `null`, quotes strings inside arrays and
  objects, and joins arguments with one space.
- New builtins: `sqrt`, `pow`, `exp`, `log`, `tan`, `floor`, `ceil`, `round`,
  `sum`, `sorted`, `random`, `random_range`, `random_int`, `clock`, `bool`,
  `type_of`, `keys`, `values`, `has`, `contains`, `join`, `split`, `env`.
- CLI: `--check`, `--tokens`, `--ast`, `--no-sleep` (or `MYCELIUM_NO_SLEEP=1`),
  `--seed N`, `--traceback`, and `-` to read a program from standard input.
  `--help` is plain text. Exit codes: 0 ran, 1 error, 2 no file given.
- Python API: `mycelium_ei.run_file`, `run_source`, `Interpreter(write=,
  no_sleep=, seed=)`, `parse`, `tokenize`.
- A test suite (134 tests) covering the lexer, parser, interpreter, builtins,
  the CLI, every example program, and the absence of third-party imports.

### Changed

- The optimizers (`genetic_optimize`, `swarm_optimize`, `ant_optimize`,
  `bio_compare`) are pure Python; particle swarm and ant colony no longer use
  numpy. Results differ numerically from 0.1.x runs.
- A fitness function may take one array parameter or one parameter per
  dimension; it must return a number.
- `add_node()` connects each new node to the previously added node, so
  `broadcast_signal` reaches the nodes an example creates. Node ids are
  `node_01`, `node_02`, ... instead of random UUID prefixes.
- `get_env` of an undeclared parameter is an error instead of returning 0.0.
- Assigning to a variable that was never declared with `let` is an error.
- Builtin output lines no longer contain emoji.
- `requires-python` is `>=3.9`. Tested on CPython 3.9 through 3.14 on macOS.
- `examples/network_demo.myc` prints the node and connection counts instead of
  the whole statistics object.

### Removed

- `mycelium_interpreter.py`, `bio_algorithms.py`, `bio_ml_integration.py`,
  `cultivation_monitor.py` and `network_framework.py` at the repository root.
  Their code moved into the `mycelium_ei` package.
- `setup.py`.

## 0.1.2 (2025-09-14), 0.1.1 and 0.1.0 (2025-09-12)

First uploads. Broken as described under 0.2.0: the installed command could
not run any `.myc` file.
