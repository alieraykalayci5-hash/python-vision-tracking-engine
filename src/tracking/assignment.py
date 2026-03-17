import numpy as np
from scipy.optimize import linear_sum_assignment

from src.tracking.utils import bbox_center, euclidean_distance


def build_cost_matrix(tracks, detections):
    if len(tracks) == 0 or len(detections) == 0:
        return np.empty((0, 0), dtype=float)

    cost_matrix = np.zeros((len(tracks), len(detections)), dtype=float)

    for i, track in enumerate(tracks):
        track_pos = track.get_position()

        for j, det in enumerate(detections):
            det_center = bbox_center(det["bbox"])
            cost_matrix[i, j] = euclidean_distance(track_pos, det_center)

    return cost_matrix


def hungarian_assignment(tracks, detections, max_distance):
    if len(tracks) == 0:
        return [], [], list(range(len(detections)))

    if len(detections) == 0:
        return [], list(range(len(tracks))), []

    cost_matrix = build_cost_matrix(tracks, detections)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    matches = []
    unmatched_tracks = set(range(len(tracks)))
    unmatched_detections = set(range(len(detections)))

    for track_idx, det_idx in zip(row_ind, col_ind):
        distance = cost_matrix[track_idx, det_idx]

        if distance <= max_distance:
            matches.append((track_idx, det_idx))
            unmatched_tracks.discard(track_idx)
            unmatched_detections.discard(det_idx)

    return matches, sorted(list(unmatched_tracks)), sorted(list(unmatched_detections))