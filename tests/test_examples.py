"""Every program in examples/ must run to completion under the packaged interpreter."""

import subprocess
import sys

import pytest

from conftest import EXAMPLES, ROOT

EXPECTED = {
    "hello_world.myc": ["Hello from the Mycelium Network!", "Optimal growth conditions detected"],
    "debug_test.myc": ["Function result: 10.0", "Debug test complete"],
    "simple_cultivation.myc": ["Cycle:  0", "Environmental change: Temperature increased to 26", "Cultivation monitoring complete"],
    "cultivation.myc": ["Cycle:  50", "Network signal: stress_response = false", "Cultivation monitoring complete"],
    "network_simple.myc": ["Added node node_01 to network", "Environment update: temperature = 26.0", "Demo completed successfully!"],
    "network_demo.myc": ["Connected node_01 <-> node_02", "Node node_02: Received growth signal", "  Nodes: 3", "  Connections: 2"],
    "bio_simple_demo.myc": ["[BIO-OPT] Running GENETIC optimization...", "Genetic optimization completed!", "Demo completed successfully!"],
    "bio_optimization_demo.myc": ["=== Testing Genetic Algorithm ===", "PSO Results:", "ACO Results:", "  genetic:", "  pso:", "  aco:", "=== Demo Complete ==="],
    "bio_ml_demo.myc": ["Network created: Created bio-network 'mycelium_brain' with architecture 4-6-2", "Stress conditions prediction completed", "=== Demo Complete ==="],
    "cultivation_simple_demo.myc": ["Created cultivation system 'TestBatch_001'", "Optimization completed!", "=== Demo Complete ==="],
    "cultivation_platform_demo.myc": ["Batch Alpha: Created cultivation system 'MyceliumBatch_Alpha'", "--- Monitoring Cycle 3 ---", "=== Platform Demo Complete ==="],
    "neural_network.myc": ["Epoch 0 - loss:", "Epoch 4 - loss:", "Adapting to substrate stress: learning rate now 0.04", "Prediction for test input: [", "Training complete - Mycelial neural network ready"],
}


def all_examples():
    return sorted(p.name for p in EXAMPLES.glob("*.myc"))


def test_every_example_has_expectations():
    assert set(all_examples()) == set(EXPECTED), "add the new example to EXPECTED"


@pytest.mark.parametrize("name", all_examples())
def test_example_runs(name):
    result = subprocess.run(
        [sys.executable, "-m", "mycelium_ei", "--no-sleep", "--seed", "1", str(EXAMPLES / name)],
        capture_output=True, text=True, timeout=180, cwd=str(ROOT),
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output[-2000:]
    assert "Traceback" not in output
    for needle in EXPECTED[name]:
        assert needle in output, f"{name}: missing {needle!r} in output:\n{output[-3000:]}"


@pytest.mark.parametrize("name", all_examples())
def test_example_parses_with_check(name):
    result = subprocess.run(
        [sys.executable, "-m", "mycelium_ei", "--check", str(EXAMPLES / name)],
        capture_output=True, text=True, timeout=60, cwd=str(ROOT),
    )
    assert result.returncode == 0
    assert result.stdout.strip().endswith("syntax OK")
