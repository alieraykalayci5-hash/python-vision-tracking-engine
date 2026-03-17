from pathlib import Path
import ctypes

import numpy as np
from scipy.optimize import linear_sum_assignment

from src.tracking.utils import bbox_center, euclidean_distance


def build_cost_matrix(tracks, detections):
    if len(tracks) == 0 or len(detections) == 0:
        return np.empty((0, 0), dtype=np.float64)

    cost_matrix = np.zeros((len(tracks), len(detections)), dtype=np.float64)

    for i, track in enumerate(tracks):
        track_pos = track.get_position()

        for j, det in enumerate(detections):
            det_center = bbox_center(det["bbox"])
            cost_matrix[i, j] = euclidean_distance(track_pos, det_center)

    return cost_matrix


class HungarianCppSolver:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]
        dll_path = project_root / "cpp" / "build" / "hungarian.dll"

        self.available = False
        self.lib = None
        self.error_message = None
        self.dll_path = dll_path

        if not dll_path.exists():
            self.error_message = f"DLL not found: {dll_path}"
            return

        try:
            self.lib = ctypes.CDLL(str(dll_path))
            self.lib.solve_assignment.argtypes = [
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_double,
                ctypes.POINTER(ctypes.c_int),
            ]
            self.lib.solve_assignment.restype = ctypes.c_int
            self.available = True
        except OSError as exc:
            self.error_message = str(exc)
            self.available = False
            self.lib = None

    def solve(self, cost_matrix: np.ndarray, max_distance: float):
        if not self.available or self.lib is None:
            raise RuntimeError(
                f"C++ Hungarian backend is not available. Reason: {self.error_message}"
            )

        rows, cols = cost_matrix.shape

        if rows == 0:
            return np.array([], dtype=np.int32)

        cost_matrix = np.ascontiguousarray(cost_matrix, dtype=np.float64)
        result = np.full(rows, -1, dtype=np.int32)

        status = self.lib.solve_assignment(
            cost_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            rows,
            cols,
            float(max_distance),
            result.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        )

        if status != 0:
            raise RuntimeError(f"C++ Hungarian solver failed with status {status}")

        return result


_cpp_solver = HungarianCppSolver()


def hungarian_assignment(tracks, detections, max_distance):
    if len(tracks) == 0:
        return [], [], list(range(len(detections)))

    if len(detections) == 0:
        return [], list(range(len(tracks))), []

    cost_matrix = build_cost_matrix(tracks, detections)

    matches = []
    unmatched_tracks = set(range(len(tracks)))
    unmatched_detections = set(range(len(detections)))

    if _cpp_solver.available:
        assigned_cols = _cpp_solver.solve(cost_matrix, max_distance)

        for track_idx, det_idx in enumerate(assigned_cols):
            if det_idx >= 0:
                matches.append((track_idx, int(det_idx)))
                unmatched_tracks.discard(track_idx)
                unmatched_detections.discard(int(det_idx))
    else:
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        for track_idx, det_idx in zip(row_ind, col_ind):
            distance = cost_matrix[track_idx, det_idx]

            if distance <= max_distance:
                matches.append((track_idx, det_idx))
                unmatched_tracks.discard(track_idx)
                unmatched_detections.discard(det_idx)

    return matches, sorted(list(unmatched_tracks)), sorted(list(unmatched_detections))