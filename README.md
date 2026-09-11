# Mycelium-EI-Lang

Mycelium-EI-Lang is a prototype scripting language with a Python interpreter; programs read environment values such as temperature and humidity and call genetic, swarm and ant colony optimizers.

## Status

experimental

Development stopped on 2025-09-14 (last commit 5b53c9c; the repository has two commits). The code is kept for reference. The tree-walking interpreter at the repository root runs the simpler examples. These parts do not work:

- The packaged `mycelium_ei` module, which is what the `myc` and `mycelium` commands and PyPI releases 0.1.0 to 0.1.2 install, parses input with Python's `ast` module rather than the Mycelium grammar. `python -m mycelium_ei examples/hello_world.myc` prints `Error: invalid syntax (<unknown>, line 1)`.
- The Rust workspace does not build. `Cargo.toml` lists members `runtime`, `stdlib`, `tools/myc` and `tools/mypm` that are not in the repository, so `cargo metadata` fails on the missing manifest.
- `examples/cultivation.myc`, `examples/neural_network.myc` and `examples/bio_optimization_demo.myc` stop in the parser with `SyntaxError: Unexpected token`.
- The payment service under `crypto-payments/` is not running. Its Vercel URL answers HTTP 402.
- The documentation links in `pyproject.toml` (Read the Docs) and `docs/_config.yml` (GitHub Pages, configured for a different repository) answer 404.

## Install and first run

Run on 2026-09-10 with Python 3.13.14 on macOS, using uv for the virtual environment.

```
git clone https://github.com/MichaelCrowe11/mycelium-ei-lang
cd mycelium-ei-lang
uv venv --python 3.13 .venv
VIRTUAL_ENV=.venv uv pip install -e .
VIRTUAL_ENV=.venv uv pip install -r requirements.txt
.venv/bin/python mycelium_interpreter.py examples/hello_world.myc
```

Output:

```
Running examples/hello_world.myc...

Added node fc7072b0 to network
Hello from the Mycelium Network!
Welcome to ecological intelligence programming
Optimal growth conditions detected
```

The node id changes on every run. `pip install -e .` on its own installs no dependencies because `pyproject.toml` declares none; `mycelium_interpreter.py` imports numpy through `bio_algorithms.py`, so the `requirements.txt` step is required. Plain `pip` should behave the same as `uv pip` here, but I did not run it.

Steps not run: the Docker builds (`Dockerfile`, `Dockerfile.cuda`), the npm package, the VS Code extension, the WebAssembly demo, the conda, Homebrew and snap recipes, and anything under `crypto-payments/`.

## What runs today

- `mycelium_interpreter.py`: lexer, parser and tree-walking interpreter for the `.myc` syntax. Keywords: `environment`, `function`, `let`, `const`, `if`, `else`, `for`, `while`, `return`, plus `mycelium`, `network`, `signal` and `adapt` blocks.
- `examples/hello_world.myc`, `examples/simple_cultivation.myc`, `examples/bio_simple_demo.myc` and `examples/network_simple.myc` run to completion with the command above.
- `bio_algorithms.py`: numpy implementations of `GeneticAlgorithm`, `ParticleSwarmOptimization` and `AntColonyOptimization`.

## Limits

- This is an interpreter, not a compiler. Nothing here emits native code or WebAssembly. `compiler/` and `wasm/` are unbuilt scaffolding.
- `quantum_bio_computing.py` holds two-element complex arrays in numpy on the CPU. No quantum hardware is used and no speedup is claimed.
- `cultivation_monitor.py` generates its readings with `random.gauss`. It reads no sensors. Do not use it to run a grow room.
- There is no test suite. `pyproject.toml` points at a `tests/` directory that does not exist.
- Version strings disagree: `pyproject.toml` says 0.1.0, `mycelium_ei/__init__.py` says 0.1.1, PyPI has 0.1.2.
- `crypto-payments/`, `STRIPE_DEPLOYMENT_SUCCESS.md` and `MONETIZATION_STRATEGY.md` describe a payment service and prices from 2025 that are not live. They are not an offer.

## License and contact

Proprietary. See `LICENSE`: viewing and personal non-commercial evaluation only; no copying, modification or redistribution. The previous README said Apache 2.0; that was wrong. The LICENSE file governs.

Contact: michael@crowelogic.com
