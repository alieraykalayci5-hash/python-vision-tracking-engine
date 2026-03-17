import numpy as np


class KalmanFilter:
    def __init__(self, dt=1.0):
        self.dt = dt

        # State: [x, y, vx, vy]
        self.x = np.zeros((4, 1), dtype=float)

        self.F = np.array(
            [
                [1, 0, dt, 0],
                [0, 1, 0, dt],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            dtype=float,
        )

        self.H = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
            ],
            dtype=float,
        )

        self.P = np.eye(4, dtype=float) * 200.0
        self.Q = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 5.0, 0.0],
                [0.0, 0.0, 0.0, 5.0],
            ],
            dtype=float,
        )
        self.R = np.array(
            [
                [25.0, 0.0],
                [0.0, 25.0],
            ],
            dtype=float,
        )

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x

    def update(self, z):
        z = np.array(z, dtype=float).reshape(2, 1)

        y = z - (self.H @ self.x)
        s = self.H @ self.P @ self.H.T + self.R
        k = self.P @ self.H.T @ np.linalg.inv(s)

        self.x = self.x + (k @ y)
        i = np.eye(self.P.shape[0], dtype=float)
        self.P = (i - k @ self.H) @ self.P

        return self.x

    def get_position(self):
        return float(self.x[0, 0]), float(self.x[1, 0])