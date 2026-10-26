import numpy as np
import pytest
from src.tracking.assignment import _cpp_solver, build_cost_matrix, hungarian_assignment, scipy_assignment

class FakeTrack:
    def __init__(self, x, y): self.xy = x, y
    def get_position(self): return self.xy

def detection(x,y): return {"bbox": (x-5,y-5,x+5,y+5),"class_id": 0}

def test_empty():
    assert hungarian_assignment([], [detection(0,0)], 10) == ([], [], [0])
    assert hungarian_assignment([FakeTrack(0,0)], [], 10) == ([], [0], [])
    assert scipy_assignment(np.zeros((2, 0)), 10).tolist() == [-1, -1]
    assert scipy_assignment(np.zeros((0, 2)), 10).tolist() == []

def test_gating_maximizes_valid_matches():
    assert scipy_assignment(np.array([[1.,80.],[80.,1000.]]), 80).tolist() == [1,0]

def test_no_invalid_pairs():
    assert scipy_assignment(np.array([[101.,500.],[1.,200.]]), 100).tolist() == [-1,0]

def test_invalid_inputs():
    for matrix in [np.array([[float('nan')]]), np.array([[-1.]])]:
        with pytest.raises(ValueError): scipy_assignment(matrix, 10)
    with pytest.raises(ValueError): scipy_assignment(np.array([[1.]]), 0)

def test_track_geometry_and_unmatched():
    tracks = [FakeTrack(30,20), FakeTrack(150,20)]
    detections = [detection(31,20),detection(151,20),detection(400,100)]
    assert build_cost_matrix(tracks,detections).shape == (2,3)
    assert hungarian_assignment(tracks, detections, 20) == ([(0,0),(1,1)],[],[2])

def test_cpp_vs_scipy_when_compiled():
    if not _cpp_solver.available: pytest.skip('No optional native library')
    rng = np.random.default_rng(2026)
    cases = [np.array([[1.,80.],[80.,1000.]])]
    for rows in [1,2,4,7]:
        for cols in [1,2,3,8]: cases.append(rng.uniform(0,150,(rows,cols)))
    for costs in cases:
        py = scipy_assignment(costs, 80.)
        native = _cpp_solver.solve(costs, 80.)
        a = [(r,c) for r,c in enumerate(py) if c >= 0]
        b = [(r,c) for r,c in enumerate(native) if c >= 0]
        assert len(a)==len(b)
        assert np.isclose(sum(costs[r,c] for r,c in a),sum(costs[r,c] for r,c in b),atol=1e-7)


def test_cross_class_detections_do_not_swap_track_ids():
    # The distance-only assignment would pick (0, 0) and (1, 1).
    # Class-aware gating must match the correct class despite the crossing.
    tracks = [FakeTrack(10, 0), FakeTrack(30, 0)]
    tracks[0].class_id = 0
    tracks[1].class_id = 1
    detections = [detection(12, 0), detection(28, 0)]
    detections[0]["class_id"] = 1
    detections[1]["class_id"] = 0
    assert hungarian_assignment(tracks, detections, 40) == (
        [(0, 1), (1, 0)], [], []
    )


def test_class_gating_preserves_backward_compatibility():
    # Track objects without class metadata still use distance-only matching.
    tracks = [FakeTrack(10, 0)]
    dets = [detection(11, 0)]
    assert hungarian_assignment(tracks, dets, 40) == ([(0, 0)], [], [])
