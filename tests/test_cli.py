import subprocess
import sys

import pytest

import mycelium_ei
from conftest import EXAMPLES, ROOT


def myc(*args, stdin=None):
    return subprocess.run([sys.executable, "-m", "mycelium_ei", *args], capture_output=True, text=True,
                          input=stdin, timeout=60, cwd=str(ROOT))


def test_version_flag():
    result = myc("--version")
    assert result.returncode == 0
    assert result.stdout.strip() == f"mycelium-ei-language {mycelium_ei.__version__}"


def test_installed_metadata_version_matches_package():
    try:
        from importlib.metadata import version
        installed = version("mycelium-ei-language")
    except Exception:  # noqa: BLE001 - not installed in this environment
        pytest.skip("package not installed")
    assert installed == mycelium_ei.__version__


def test_help_is_plain_ascii_and_lists_flags():
    result = myc("--help")
    assert result.returncode == 0
    assert result.stdout.isascii()
    for flag in ("--check", "--tokens", "--ast", "--no-sleep", "--seed"):
        assert flag in result.stdout
    assert "https://github.com/MichaelCrowe11/mycelium-ei-lang" in result.stdout


def test_no_arguments_prints_help_and_exits_2():
    result = myc()
    assert result.returncode == 2
    assert "usage: myc" in result.stdout


def test_missing_file():
    result = myc("does-not-exist.myc")
    assert result.returncode == 1
    assert result.stderr.strip() == "myc: error: file not found: does-not-exist.myc"


def test_check_tokens_and_ast(tmp_path):
    program = EXAMPLES / "hello_world.myc"
    assert myc("--check", str(program)).stdout.strip() == f"{program}: syntax OK"
    tokens = myc("--tokens", str(program)).stdout
    assert tokens.splitlines()[0].split("\t")[1] == "ENVIRONMENT"
    ast = myc("--ast", str(program)).stdout
    assert ast.startswith("Program @3:1") and "FunctionDecl" in ast


def test_syntax_error_exit_code_and_message(tmp_path):
    bad = tmp_path / "bad.myc"
    bad.write_text("function main() {\n  print(1\n}\n")
    result = myc(str(bad))
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip() == f"{bad}:3:1: syntax error: Expected ')' after arguments, found '}}'"


def test_runtime_error_exit_code_and_message(tmp_path):
    bad = tmp_path / "bad.myc"
    bad.write_text('print("start")\nlet a = 1 / 0\n')
    result = myc(str(bad))
    assert result.returncode == 1
    assert result.stdout.strip() == "start"
    assert result.stderr.strip() == f"{bad}:2:9: runtime error: Division by zero"


def test_program_from_stdin():
    result = myc("-", stdin='print("from stdin", 1 + 1)')
    assert result.returncode == 0
    assert result.stdout.strip() == "from stdin 2"


def test_seed_gives_repeatable_output(tmp_path):
    prog = tmp_path / "r.myc"
    prog.write_text("print(random(), random_range(0, 10))")
    assert myc("--seed", "3", str(prog)).stdout == myc("--seed", "3", str(prog)).stdout


def test_console_script_entry_point_is_declared():
    tomllib = pytest.importorskip("tomllib")  # Python 3.11+
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert data["project"]["scripts"] == {"myc": "mycelium_ei.cli:main", "mycelium": "mycelium_ei.cli:main"}


def test_cli_supports_recursion_depth_1500(tmp_path):
    prog = tmp_path / "deep.myc"
    prog.write_text("function count(n) { if n == 0 { return 0 } return 1 + count(n - 1) }\nprint(count(1500))\n")
    result = myc(str(prog))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "1500"


def test_cli_reports_runaway_recursion_cleanly(tmp_path):
    prog = tmp_path / "forever.myc"
    prog.write_text("function f(n) { return f(n + 1) }\nf(0)\n")
    result = myc(str(prog))
    assert result.returncode == 1
    assert result.stderr.strip() == f"{prog}:1:24: runtime error: Maximum call depth (2000) exceeded in function 'f'"
    assert "Segmentation" not in result.stderr and "Traceback" not in result.stderr
