from src.tracking.assignment import hungarian_assignment
from src.tracking.track import Track
from src.tracking.utils import bbox_center


class MultiObjectTracker:
    def __init__(self, max_match_distance=80.0, max_missed_frames=10):
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
            self.tracks,
            detections,
            self.max_match_distance,
        )

        # UPDATE MATCHED
        for track_idx, det_idx in matches:
            det = detections[det_idx]
            center = bbox_center(det["bbox"])
            self.tracks[track_idx].update(center)

        # MARK MISSED
        for track_idx in unmatched_tracks:
            self.tracks[track_idx].mark_missed()

        # REMOVE DEAD TRACKS
        self.tracks = [
            t for t in self.tracks if not t.is_deleted(self.max_missed_frames)
        ]

        # CREATE NEW TRACKS (tentative)
        for det_idx in unmatched_detections:
            det = detections[det_idx]
            center = bbox_center(det["bbox"])

            new_track = Track(
                track_id=self.next_track_id,
                initial_position=center,
                n_init=3,
            )

            self.next_track_id += 1
            self.tracks.append(new_track)

        return matches

    def get_tracks(self):
        return [t for t in self.tracks if t.is_confirmed()]