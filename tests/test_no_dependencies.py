"""The package must import and run programs without any third-party module."""

import subprocess
import sys

from conftest import EXAMPLES, ROOT


def test_importing_the_package_pulls_in_no_third_party_modules():
    code = (
        "import sys, mycelium_ei, mycelium_ei.bio.algorithms, mycelium_ei.bio.ml, "
        "mycelium_ei.bio.cultivation, mycelium_ei.network;"
        "third = sorted(m for m in ('numpy', 'scipy', 'numba', 'lz4') if m in sys.modules);"
        "print(third)"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=str(ROOT))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"


def test_examples_run_with_numpy_blocked():
    code = (
        "import sys; sys.modules['numpy'] = None; sys.modules['scipy'] = None;"
        "from mycelium_ei.cli import main;"
        f"sys.exit(main(['--no-sleep', '--seed', '1', r'{EXAMPLES / 'bio_optimization_demo.myc'}']))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=str(ROOT), timeout=180)
    assert result.returncode == 0, result.stderr[-2000:]
    assert "=== Demo Complete ===" in result.stdout
