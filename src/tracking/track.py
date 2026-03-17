from src.tracking.kalman_filter import KalmanFilter


class Track:
    def __init__(self, track_id: int, initial_position, n_init=3):
        self.id = track_id
        self.kf = KalmanFilter()

        x, y = initial_position
        self.kf.x[0, 0] = x
        self.kf.x[1, 0] = y

        self.missed = 0
        self.age = 1

        self.hits = 1
        self.n_init = n_init

        self.confirmed = False

        self.history = []
        self.max_history = 20

        self._append_history()

    def _append_history(self):
        pos = self.get_position()
        self.history.append(pos)

        if len(self.history) > self.max_history:
            self.history.pop(0)

    def predict(self):
        self.age += 1
        self.kf.predict()
        self._append_history()
        return self.kf.x

    def update(self, position):
        self.kf.update(position)
        self.missed = 0
        self.hits += 1

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