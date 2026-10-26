from src.tracking.assignment import hungarian_assignment
from src.tracking.track import Track
from src.tracking.utils import bbox_center


class MultiObjectTracker:
    def __init__(self, max_match_distance=80.0, max_missed_frames=10):
        if max_match_distance <= 0 or max_missed_frames < 0:
            raise ValueError("Invalid tracking configuration")
        self.max_match_distance = max_match_distance
        self.max_missed_frames = max_missed_frames
        self.tracks = []
        self.next_track_id = 1

    def predict(self):
        for track in self.tracks:
            track.predict()

    def update(self, detections):
        self.predict()
        matches, unmatched_tracks, unmatched_detections = hungarian_assignment(
            self.tracks, detections, self.max_match_distance
        )
        for track_idx, det_idx in matches:
            bbox = detections[det_idx]["bbox"]
            self.tracks[track_idx].update(bbox_center(bbox), bbox=bbox)
        for track_idx in unmatched_tracks:
            self.tracks[track_idx].mark_missed()
        self.tracks = [t for t in self.tracks if not t.is_deleted(self.max_missed_frames)]
        for det_idx in unmatched_detections:
            bbox = detections[det_idx]["bbox"]
            self.tracks.append(Track(
                track_id=self.next_track_id,
                initial_position=bbox_center(bbox),
                n_init=3,
                bbox=bbox,
                class_id=detections[det_idx].get("class_id"),
            ))
            self.next_track_id += 1
        return matches, unmatched_tracks, unmatched_detections

    def get_tracks(self):
        return [t for t in self.tracks if t.is_confirmed()]
