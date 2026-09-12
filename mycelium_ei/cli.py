"""Command-line entry point: ``myc`` and ``mycelium``."""

from __future__ import annotations

import argparse
import dataclasses
import sys
from typing import Any, List, Optional

from . import __version__
from .errors import MyceliumError
from .interpreter import CLI_MAX_CALL_DEPTH, Interpreter, run_in_thread
from .lexer import tokenize
from .parser import parse

REPOSITORY = "https://github.com/MichaelCrowe11/mycelium-ei-lang"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="myc",
        description="Run a Mycelium-EI-Lang program (a .myc file).",
        epilog=f"Language reference and examples: {REPOSITORY}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", nargs="?", help="program to run; use '-' to read from standard input")
    parser.add_argument("--version", action="version", version=f"mycelium-ei-language {__version__}")
    parser.add_argument("--check", action="store_true", help="parse the program and report syntax errors without running it")
    parser.add_argument("--tokens", action="store_true", help="print the token stream instead of running")
    parser.add_argument("--ast", action="store_true", help="print the syntax tree instead of running")
    parser.add_argument("--no-sleep", action="store_true", help="make sleep() return at once (also MYCELIUM_NO_SLEEP=1)")
    parser.add_argument("--seed", type=int, metavar="N", help="seed the random number generator for repeatable runs")
    parser.add_argument("--traceback", action="store_true", help="show the Python traceback for interpreter errors")
    return parser


def read_source(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def dump_ast(node: Any, indent: int = 0, out: Optional[List[str]] = None) -> List[str]:
    """Render a syntax tree as an indented outline."""
    lines = out if out is not None else []
    pad = "  " * indent
    if dataclasses.is_dataclass(node) and not isinstance(node, type):
        name = type(node).__name__
        scalars = []
        children = []
        for field in dataclasses.fields(node):
            if field.name in ("line", "column"):
                continue
            value = getattr(node, field.name)
            if dataclasses.is_dataclass(value) or (isinstance(value, list) and value and
                                                   any(dataclasses.is_dataclass(v) or isinstance(v, tuple) for v in value)):
                children.append((field.name, value))
            elif isinstance(value, list) and not value:
                scalars.append(f"{field.name}=[]")
            else:
                scalars.append(f"{field.name}={value!r}")
        position = f" @{node.line}:{node.column}" if hasattr(node, "line") else ""
        lines.append(f"{pad}{name}{position}" + (" " + " ".join(scalars) if scalars else ""))
        for field_name, value in children:
            lines.append(f"{pad}  {field_name}:")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, tuple):
                        lines.append(f"{pad}    {item[0]}:")
                        dump_ast(item[1], indent + 3, lines)
                    else:
                        dump_ast(item, indent + 2, lines)
            else:
                dump_ast(value, indent + 2, lines)
    else:
        lines.append(f"{pad}{node!r}")
    return lines


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.file is None:
        parser.print_help()
        return 2
    filename = "<stdin>" if args.file == "-" else args.file
    try:
        source = read_source(args.file)
    except FileNotFoundError:
        print(f"myc: error: file not found: {args.file}", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"myc: error: {args.file} is a directory, not a .myc file", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"myc: error: cannot read {args.file}: {exc.strerror}", file=sys.stderr)
        return 1

    try:
        if args.tokens:
            for token in tokenize(source, filename):
                print(f"{token.line}:{token.column}\t{token.type.name}\t{token.value!r}")
            return 0
        program = parse(source, filename)
        if args.ast:
            print("\n".join(dump_ast(program)))
            return 0
        if args.check:
            print(f"{filename}: syntax OK")
            return 0
        interpreter = Interpreter(filename, no_sleep=True if args.no_sleep else None, seed=args.seed,
                                  max_call_depth=CLI_MAX_CALL_DEPTH)
        run_in_thread(lambda: interpreter.execute(program))
        return 0
    except MyceliumError as err:
        if err.filename is None:
            err.filename = filename
        if args.traceback:
            import traceback
            traceback.print_exc()
        print(err.format(), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nmyc: interrupted", file=sys.stderr)
        return 130
    except RecursionError:
        print(f"{filename}: runtime error: maximum recursion depth exceeded", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
