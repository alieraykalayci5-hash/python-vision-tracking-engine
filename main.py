"""Video object-tracking entry point.

Run `python main.py --help` for command-line usage.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

import config
from src.io.video_reader import VideoReader
from src.io.video_writer import VideoWriter
from src.tracking.assignment import _cpp_solver
from src.tracking.tracker import MultiObjectTracker
from src.visualization.draw import draw_tracks


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="YOLO + Kalman multi-object tracker")
    parser.add_argument("--input", default=config.VIDEO_SOURCE,
                        help="Video filepath, or integer camera index (e.g. 0)")
    parser.add_argument("--output", default=config.OUTPUT_VIDEO_PATH,
                        help="Output MP4 filepath")
    parser.add_argument("--model", default="yolov8n.pt",
                        help="YOLO model path/name; may download on first use")
    parser.add_argument("--confidence", type=float, default=0.4)
    parser.add_argument("--class-id", type=int, default=0,
                        help="COCO class ID to track; default 0 (person)")
    parser.add_argument("--all-classes", action="store_true",
                        help="Track detections of all classes")
    parser.add_argument("--headless", action="store_true",
                        help="Do not create a GUI window")
    parser.add_argument("--no-save", action="store_true", help="Do not write MP4")
    parser.add_argument("--max-match-distance", type=float, default=80.0)
    parser.add_argument("--max-missed-frames", type=int, default=10)
    parser.add_argument("--max-frames", type=int, default=0,
                        help="Limit processed frames (0 means unlimited)")
    args = parser.parse_args(argv)
    if not 0 < args.confidence <= 1:
        parser.error("--confidence must be in (0, 1]")
    if args.max_match_distance <= 0 or args.max_missed_frames < 0 or args.max_frames < 0:
        parser.error("Invalid tracking limits")
    if args.class_id < 0:
        parser.error("--class-id must be >= 0")
    return args


def ensure_directories(output_path: str):
    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    Path(output_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def validate_input_video(source: str):
    if source.isdecimal():
        return int(source)
    if not Path(source).expanduser().is_file():
        raise FileNotFoundError(
            f"Input video not found: {source}\n"
            "Place a video in data/input/, or pass --input PATH. "
            "You can also generate a synthetic example with "
            "python tools/make_synthetic_demo.py"
        )
    return str(Path(source).expanduser())


def main(argv=None):
    args = parse_args(argv)
    ensure_directories(args.output)
    video_source = validate_input_video(args.input)

    # Delayed import: lightweight unit tests and --help need no PyTorch installation.
    from src.detection.yolo_detector import YOLODetector

    reader = None
    writer = None
    frames_processed = 0
    start = time.perf_counter()
    display = not args.headless
    try:
        reader = VideoReader(video_source)
        detector = YOLODetector(model_name=args.model, conf_threshold=args.confidence)
        tracker = MultiObjectTracker(
            max_match_distance=args.max_match_distance,
            max_missed_frames=args.max_missed_frames,
        )
        if not args.no_save:
            writer = VideoWriter(args.output, reader.get_fps(),
                                 reader.get_width(), reader.get_height())
        backend = "C++ native" if _cpp_solver.available else "SciPy"
        print(f"[INFO] Input: {args.input} | Assignment backend: {backend}")
        if writer:
            print(f"[INFO] Output: {args.output}")
        last_frame_time = None
        while True:
            ok, frame = reader.read()
            if not ok:
                break
            detections = detector.detect(frame)
            if not args.all_classes:
                detections = [d for d in detections if d["class_id"] == args.class_id]
            tracker.update(detections)
            tracks = tracker.get_tracks()
            frame = draw_tracks(frame, tracks)
            now = time.perf_counter()
            instantaneous_fps = 1.0 / (now - last_frame_time) if last_frame_time else 0.0
            last_frame_time = now
            cv2.putText(frame, f"FPS: {instantaneous_fps:.1f}", (18, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Tracks: {len(tracks)}", (18, 72),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if writer:
                writer.write(frame)
            if display:
                cv2.imshow(config.DISPLAY_WINDOW_NAME, frame)
                if cv2.waitKey(1) & 0xFF == config.EXIT_KEY:
                    print("[INFO] Stopped by user")
                    break
            frames_processed += 1
            if args.max_frames and frames_processed >= args.max_frames:
                break
    finally:
        if reader is not None:
            reader.release()
        if writer is not None:
            writer.release()
        if display:
            cv2.destroyAllWindows()
        elapsed = time.perf_counter() - start
        print(f"[INFO] Processed {frames_processed} frames in {elapsed:.2f}s "
              f"({frames_processed / elapsed:.2f} end-to-end FPS, includes setup)" if elapsed else
              f"[INFO] Processed {frames_processed} frames")
    return frames_processed


if __name__ == "__main__":
    main()
