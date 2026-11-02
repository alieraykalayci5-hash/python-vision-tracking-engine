"""Reproducible *assignment-only* microbenchmark (not YOLO/tracker FPS).

Run from the repository root::

    python -m tools.benchmark_assignment --sizes 10 30 60 --iterations 30

Synthetic costs are generated from a fixed seed. Both implementations receive
identical matrices, and match count/total cost are checked for parity.
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

import numpy as np
import scipy

from src.tracking.assignment import HungarianCppSolver, scipy_assignment


def make_cost_matrices(size: int, count: int, seed: int, max_distance: float):
    """Produce deterministic, nonnegative square cost matrices with gated pairs."""
    if size < 1 or count < 1 or not np.isfinite(max_distance) or max_distance <= 0:
        raise ValueError("Size/count must be positive and max_distance finite and positive")
    rng = np.random.default_rng(seed)
    return [rng.uniform(0, max_distance * 1.5, size=(size, size))
            for _ in range(count)]


def assignment_score(costs: np.ndarray, assigned: np.ndarray):
    """Return (valid match count, total matching cost) for parity checking."""
    matches = [(i, int(j)) for i, j in enumerate(assigned) if j >= 0]
    return len(matches), sum(float(costs[i, j]) for i, j in matches)


def measure(solve, matrices, warmups, max_distance):
    """Report measured solver time; exclude warmup calls from reported samples."""
    latencies_ms = []
    results = []
    for i, costs in enumerate(matrices):
        start = time.perf_counter_ns()
        result = solve(costs, max_distance)
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        if i >= warmups:
            latencies_ms.append(elapsed_ms)
            results.append(result)
    return {
        "median_ms": statistics.median(latencies_ms),
        "p95_ms": float(np.percentile(latencies_ms, 95)),
        "samples": len(latencies_ms),
    }, results


def run_benchmark(sizes=(10, 30, 60), iterations=30, warmups=5,
                  max_distance=80.0, seed=2026, solver=None):
    """Run microbenchmarks; native backend is optional and never silently faked."""
    if iterations < 1 or warmups < 0:
        raise ValueError("iterations >= 1 and warmups >= 0 are required")
    if not sizes or any(size < 1 for size in sizes):
        raise ValueError("sizes must contain positive integers")
    if not np.isfinite(max_distance) or max_distance <= 0:
        raise ValueError("max_distance must be finite and positive")
    if solver is None:
        solver = HungarianCppSolver()

    report = {
        "kind": "synthetic_assignment_only",
        "warning": "Not YOLO FPS, full tracking FPS, or MOT accuracy. Results are hardware-specific.",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "seed": seed,
        "iterations": iterations,
        "warmups": warmups,
        "max_distance": max_distance,
        "native_available": bool(solver.available),
        "cases": [],
    }
    for size in sizes:
        # Vary the generated input by size, while keeping it deterministic.
        matrices = make_cost_matrices(size, iterations + warmups,
                                     seed + size, max_distance)
        scipy_stats, scipy_results = measure(
            scipy_assignment, matrices, warmups, max_distance)
        case = {"size": size, "scipy": scipy_stats, "cpp": None}
        if solver.available:
            native_stats, native_results = measure(
                solver.solve, matrices, warmups, max_distance)
            for costs, left, right in zip(matrices[warmups:],
                                          scipy_results, native_results):
                count_py, cost_py = assignment_score(costs, left)
                count_cpp, cost_cpp = assignment_score(costs, right)
                if count_py != count_cpp or not np.isclose(cost_py, cost_cpp, rtol=1e-7, atol=1e-7):
                    raise RuntimeError(f"C++/SciPy assignment mismatch for size={size}")
            case["cpp"] = native_stats
        report["cases"].append(case)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[10, 30, 60])
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--max-distance", type=float, default=80.0)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--json-output", type=Path, help="Optional JSON report file")
    args = parser.parse_args(argv)
    try:
        report = run_benchmark(args.sizes, args.iterations, args.warmups,
                               args.max_distance, args.seed)
    except ValueError as error:
        parser.error(str(error))
    text = json.dumps(report, indent=2)
    print(text)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(text + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    main()
