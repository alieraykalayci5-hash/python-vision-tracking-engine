import json

import numpy as np
import pytest

from tools.benchmark_assignment import (
    assignment_score,
    main,
    make_cost_matrices,
    run_benchmark,
)


class UnavailableNative:
    available = False


def test_synthetic_cost_generation_is_reproducible():
    left = make_cost_matrices(4, 3, seed=100, max_distance=80)
    right = make_cost_matrices(4, 3, seed=100, max_distance=80)
    assert len(left) == 3
    assert all(np.array_equal(a, b) for a, b in zip(left, right))
    assert left[0].shape == (4, 4)
    assert np.all(left[0] >= 0)


def test_benchmark_without_native_backend():
    report = run_benchmark(sizes=(3, 5), iterations=3, warmups=1,
                           seed=42, solver=UnavailableNative())
    assert report["kind"] == "synthetic_assignment_only"
    assert report["native_available"] is False
    assert [item["size"] for item in report["cases"]] == [3, 5]
    assert all(item["scipy"]["samples"] == 3 for item in report["cases"])
    assert all(item["scipy"]["p95_ms"] >= 0 for item in report["cases"])
    assert all(item["cpp"] is None for item in report["cases"])


def test_assignment_score():
    costs = np.array([[3.0, 5.0], [7.0, 2.0]])
    assert assignment_score(costs, np.array([0, 1])) == (2, 5.0)
    assert assignment_score(costs, np.array([-1, 1])) == (1, 2.0)


@pytest.mark.parametrize("settings", [
    {"sizes": [0]},
    {"iterations": 0},
    {"warmups": -1},
    {"max_distance": float("nan")},
    {"max_distance": 0.0},
])
def test_benchmark_rejects_invalid_parameters(settings):
    with pytest.raises(ValueError):
        run_benchmark(solver=UnavailableNative(), **settings)


def test_cli_writes_json(tmp_path):
    target = tmp_path / "reports" / "assignment.json"
    result = main(["--sizes", "3", "--iterations", "2", "--warmups", "0",
                   "--json-output", str(target)])
    assert target.is_file()
    stored = json.loads(target.read_text(encoding="utf-8"))
    assert stored["seed"] == result["seed"]
    assert stored["cases"][0]["scipy"]["samples"] == 2


class EquivalentNative:
    available = True

    @staticmethod
    def solve(costs, max_distance):
        from src.tracking.assignment import scipy_assignment
        return scipy_assignment(costs, max_distance)


class IncorrectNative:
    available = True

    @staticmethod
    def solve(costs, max_distance):
        return np.full(costs.shape[0], -1, dtype=int)


def test_native_parity_success_path():
    result = run_benchmark(sizes=(4,), iterations=2, warmups=1,
                           solver=EquivalentNative())
    assert result["native_available"] is True
    assert result["cases"][0]["cpp"]["samples"] == 2


def test_native_mismatch_is_detected():
    with pytest.raises(RuntimeError, match="mismatch"):
        run_benchmark(sizes=(4,), iterations=2, warmups=0,
                      solver=IncorrectNative())
