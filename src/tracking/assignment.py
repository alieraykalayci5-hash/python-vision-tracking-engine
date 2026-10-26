"""Gate-aware bipartite assignment with optional C++ acceleration.

Unmatched tracks and detections are represented by dummy nodes, ensuring that
unacceptable matches do not displace valid matches before post-filtering.
"""
from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

from src.tracking.utils import bbox_center, euclidean_distance


def build_cost_matrix(tracks, detections, max_distance=None):
    cost_matrix = np.zeros((len(tracks), len(detections)), dtype=np.float64)
    for i, track in enumerate(tracks):
        for j, detection in enumerate(detections):
            # Never pair different known detection classes. Missing class IDs
            # retain the legacy distance-only behavior for compatibility.
            track_class = getattr(track, "class_id", None)
            detection_class = detection.get("class_id")
            if (max_distance is not None and track_class is not None
                    and detection_class is not None and track_class != detection_class):
                cost_matrix[i, j] = max_distance + 1.0
                continue
            cost_matrix[i, j] = euclidean_distance(
                track.get_position(), bbox_center(detection["bbox"])
            )
    return cost_matrix


def _validate_costs(cost_matrix, max_distance):
    costs = np.asarray(cost_matrix, dtype=np.float64)
    if costs.ndim != 2:
        raise ValueError("Cost matrix must have exactly two dimensions")
    if not np.isfinite(costs).all() or np.any(costs < 0):
        raise ValueError("Costs must be finite non-negative numbers")
    if not np.isfinite(max_distance) or max_distance <= 0:
        raise ValueError("max_distance must be finite and positive")
    return costs


def scipy_assignment(cost_matrix: np.ndarray, max_distance: float):
    """Maximize valid match count, then minimize distance for valid matches."""
    costs = _validate_costs(cost_matrix, max_distance)
    rows, cols = costs.shape
    if not rows:
        return np.empty(0, dtype=np.int32)
    if not cols:
        return np.full(rows, -1, dtype=np.int32)

    # A sufficiently large unmatched cost prioritizes number of valid pairs.
    n = rows + cols
    unmatched_cost = (min(rows, cols) + 1) * (float(max_distance) + 1)
    forbidden_cost = (2 * n + 1) * unmatched_cost
    padded = np.zeros((n, n), dtype=np.float64)
    padded[:rows, :cols] = np.where(
        costs <= max_distance, costs, forbidden_cost
    )
    padded[:rows, cols:] = unmatched_cost
    padded[rows:, :cols] = unmatched_cost
    assignments = np.full(rows, -1, dtype=np.int32)
    assigned_rows, assigned_cols = linear_sum_assignment(padded)
    for r, c in zip(assigned_rows, assigned_cols):
        if r < rows and c < cols and costs[r, c] <= max_distance:
            assignments[r] = c
    return assignments


class HungarianCppSolver:
    """Optional native backend. Missing native library is not an error."""

    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]
        name = "hungarian.dll" if sys.platform == "win32" else (
            "libhungarian.dylib" if sys.platform == "darwin" else "libhungarian.so"
        )
        self.library_path = project_root / "cpp" / "build" / name
        self.available = False
        self.lib = None
        self.error_message = None
        if os.environ.get("PVTE_FORCE_SCIPY") == "1":
            self.error_message = "Disabled by PVTE_FORCE_SCIPY=1"
            return
        if not self.library_path.exists():
            self.error_message = f"Native library not found: {self.library_path}"
            return
        try:
            lib = ctypes.CDLL(str(self.library_path))
            lib.solve_assignment.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_int, ctypes.c_int, ctypes.c_double,
                ctypes.POINTER(ctypes.c_int),
            ]
            lib.solve_assignment.restype = ctypes.c_int
            self.lib = lib
            self.available = True
        except OSError as exc:
            self.error_message = str(exc)

    def solve(self, cost_matrix: np.ndarray, max_distance: float):
        costs = _validate_costs(cost_matrix, max_distance)
        if not self.available or self.lib is None:
            raise RuntimeError(f"Native backend unavailable: {self.error_message}")
        rows, cols = costs.shape
        if rows == 0:
            return np.empty(0, dtype=np.int32)
        if cols == 0:
            return np.full(rows, -1, dtype=np.int32)
        costs = np.ascontiguousarray(costs, dtype=np.float64)
        output = np.full(rows, -1, dtype=np.int32)
        status = self.lib.solve_assignment(
            costs.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            rows, cols, float(max_distance),
            output.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        )
        if status != 0:
            raise RuntimeError(f"Native solver returned failure: {status}")
        return output


_cpp_solver = HungarianCppSolver()


def hungarian_assignment(tracks, detections, max_distance):
    """Return matches, unmatched track indexes, unmatched detection indexes."""
    if not tracks:
        return [], [], list(range(len(detections)))
    if not detections:
        return [], list(range(len(tracks))), []
    costs = build_cost_matrix(tracks, detections, max_distance=max_distance)
    if _cpp_solver.available:
        try:
            assigned = _cpp_solver.solve(costs, max_distance)
        except RuntimeError:
            assigned = scipy_assignment(costs, max_distance)
    else:
        assigned = scipy_assignment(costs, max_distance)
    matches = sorted((int(r), int(c)) for r, c in enumerate(assigned) if c >= 0)
    used_rows = {r for r, _ in matches}
    used_cols = {c for _, c in matches}
    return (matches,
            [r for r in range(len(tracks)) if r not in used_rows],
            [c for c in range(len(detections)) if c not in used_cols])
