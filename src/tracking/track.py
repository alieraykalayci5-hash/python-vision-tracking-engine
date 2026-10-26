"""Kalman-backed track state, including last measured box dimensions."""
from src.tracking.kalman_filter import KalmanFilter


class Track:
    def __init__(self, track_id: int, initial_position, n_init=3, bbox=None, class_id=None):
        if n_init < 1:
            raise ValueError("n_init must be positive")
        self.id = track_id
        # Preserve the detector class to prevent cross-class identity switches.
        self.class_id = class_id
        self.kf = KalmanFilter()
        x, y = initial_position
        self.kf.x[0, 0] = x
        self.kf.x[1, 0] = y
        self.missed = 0
        self.age = 1
        self.hits = 1
        self.n_init = n_init
        self.confirmed = n_init == 1
        self.history = []
        self.max_history = 20
        self.bbox_size = self._bbox_size(bbox) if bbox is not None else (60, 60)
        self._append_history()

    @staticmethod
    def _bbox_size(bbox):
        x1, y1, x2, y2 = bbox
        return max(1, int(x2 - x1)), max(1, int(y2 - y1))

    def _append_history(self):
        self.history.append(self.get_position())
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def predict(self):
        self.age += 1
        self.kf.predict()
        self._append_history()
        return self.kf.x

    def update(self, position, bbox=None):
        self.kf.update(position)
        self.missed = 0
        self.hits += 1
        if bbox is not None:
            self.bbox_size = self._bbox_size(bbox)
        if self.hits >= self.n_init:
            self.confirmed = True
        self._append_history()

    def mark_missed(self):
        self.missed += 1

    def is_deleted(self, max_missed):
        return self.missed > max_missed

    def is_confirmed(self):
        return self.confirmed

    def get_position(self):
        return self.kf.get_position()

    def get_bbox(self):
        """Estimated bounding box at predicted/updated centre (w/h last seen)."""
        x, y = self.get_position()
        width, height = self.bbox_size
        return (int(round(x - width / 2)), int(round(y - height / 2)),
                int(round(x + width / 2)), int(round(y + height / 2)))
