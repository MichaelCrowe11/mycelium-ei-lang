"""Mycelium-EI-Lang: a small interpreted language for cultivation models.

Programs declare environment parameters, react to them with ``adapt``
functions, and call genetic, particle swarm and ant colony optimizers.

Copyright (c) 2024-2026 Michael Benjamin Crowe. Proprietary; see LICENSE.
"""

__version__ = "0.2.0"
__author__ = "Michael Benjamin Crowe"
__license__ = "Proprietary"

from .errors import MyceliumError, MyceliumRuntimeError, MyceliumSyntaxError  # noqa: E402
from .interpreter import Interpreter, run_file, run_source  # noqa: E402
from .lexer import tokenize  # noqa: E402
from .parser import parse  # noqa: E402
from .values import format_value  # noqa: E402


def main(argv=None):
    """Console entry point (``myc``, ``mycelium``, ``python -m mycelium_ei``)."""
    from .cli import main as _main
    return _main(argv)


__all__ = [
    "__version__",
    "Interpreter",
    "MyceliumError",
    "MyceliumRuntimeError",
    "MyceliumSyntaxError",
    "format_value",
    "main",
    "parse",
    "run_file",
    "run_source",
    "tokenize",
]
