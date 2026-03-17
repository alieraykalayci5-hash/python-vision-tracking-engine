from pathlib import Path
import time

import cv2

import config
from src.detection.yolo_detector import YOLODetector
from src.io.video_reader import VideoReader
from src.io.video_writer import VideoWriter
from src.tracking.tracker import MultiObjectTracker
from src.visualization.draw import draw_tracks


PERSON_CLASS_ID = 0


def ensure_directories() -> None:
    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    config.FRAMES_DIR.mkdir(parents=True, exist_ok=True)


def validate_input_video() -> None:
    video_path = Path(config.VIDEO_SOURCE)
    if not video_path.exists():
        raise FileNotFoundError(f"Input video not found: {video_path}")


def filter_person_detections(detections):
    return [det for det in detections if det["class_id"] == PERSON_CLASS_ID]


def main() -> None:
    ensure_directories()
    validate_input_video()

    reader = VideoReader(config.VIDEO_SOURCE)
    detector = YOLODetector(model_name="yolov8n.pt", conf_threshold=0.4)
    tracker = MultiObjectTracker(max_match_distance=80.0, max_missed_frames=10)

    width = reader.get_width()
    height = reader.get_height()
    video_fps = reader.get_fps()

    writer = None
    if config.SAVE_OUTPUT:
        writer = VideoWriter(
            output_path=config.OUTPUT_VIDEO_PATH,
            fps=video_fps,
            width=width,
            height=height,
        )

    print("[INFO] Improved Multi-object Tracking")
    print(f"[INFO] Input video: {config.VIDEO_SOURCE}")
    print(f"[INFO] Output video: {config.OUTPUT_VIDEO_PATH}")
    print("[INFO] Press 'q' to quit.")

    prev_time = 0.0

    try:
        while True:
            ret, frame = reader.read()
            if not ret:
                print("[INFO] End of video reached.")
                break

            detections = detector.detect(frame)
            detections = filter_person_detections(detections)

            tracker.update(detections)
            tracks = tracker.get_tracks()

            frame = draw_tracks(frame, tracks)

            current_time = time.time()
            fps = 1.0 / (current_time - prev_time) if prev_time > 0 else 0.0
            prev_time = current_time

            cv2.putText(
                frame,
                f"FPS: {int(fps)}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"Active Tracks: {len(tracks)}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            if config.SHOW_VIDEO:
                cv2.imshow(config.DISPLAY_WINDOW_NAME, frame)

            if writer is not None:
                writer.write(frame)

            if cv2.waitKey(1) & 0xFF == config.EXIT_KEY:
                print("[INFO] Exit requested by user.")
                break

    finally:
        reader.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()
        print("[INFO] Resources released cleanly.")


if __name__ == "__main__":
    main()