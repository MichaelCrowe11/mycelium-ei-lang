import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"

os.environ.setdefault("MYCELIUM_NO_SLEEP", "1")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def run():
    """Run source and return the printed lines."""
    from mycelium_ei.interpreter import Interpreter

    def _run(source: str, **options):
        lines = []
        interp = Interpreter("<test>", write=lines.append, no_sleep=True, **options)
        interp.run(source)
        return lines

    return _run


@pytest.fixture
def interp_run():
    """Run source and return (interpreter, printed lines)."""
    from mycelium_ei.interpreter import Interpreter

    def _run(source: str, **options):
        lines = []
        interp = Interpreter("<test>", write=lines.append, no_sleep=True, **options)
        interp.run(source)
        return interp, lines

    return _run
