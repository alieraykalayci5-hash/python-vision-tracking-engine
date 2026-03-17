import cv2


def draw_tracks(frame, tracks):
    for track in tracks:
        x, y = track.get_position()
        x_i, y_i = int(x), int(y)

        # Bounding box (fake size ama yeterli)
        box_size = 60
        x1 = x_i - box_size // 2
        y1 = y_i - box_size // 2
        x2 = x_i + box_size // 2
        y2 = y_i + box_size // 2

        # Kutu
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Trail
        for i in range(1, len(track.history)):
            pt1 = (int(track.history[i - 1][0]), int(track.history[i - 1][1]))
            pt2 = (int(track.history[i][0]), int(track.history[i][1]))
            cv2.line(frame, pt1, pt2, (255, 0, 0), 2)

        # Merkez nokta
        cv2.circle(frame, (x_i, y_i), 4, (0, 0, 255), -1)

        # ID
        cv2.putText(
            frame,
            f"ID {track.id}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    return frame