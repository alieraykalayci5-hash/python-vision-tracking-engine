"""Frame overlays for confirmed tracks."""
import cv2


def draw_tracks(frame, tracks):
    for track in tracks:
        x, y = track.get_position()
        x_i, y_i = int(round(x)), int(round(y))
        x1, y1, x2, y2 = track.get_bbox()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        for previous, current in zip(track.history, track.history[1:]):
            a = tuple(round(v) for v in previous)
            b = tuple(round(v) for v in current)
            cv2.line(frame, a, b, (255, 0, 0), 2)
        cv2.circle(frame, (x_i, y_i), 4, (0, 0, 255), -1)
        cv2.putText(frame, f"ID {track.id}", (x1, max(15, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
    return frame
