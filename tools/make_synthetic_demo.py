"""Create an original, generated test clip; no third-party footage needed.

This draws geometric shapes, not photographic people. YOLO may detect zero
persons: the clip tests I/O, it does NOT demonstrate tracking quality.
"""
from pathlib import Path
import argparse
import cv2
import numpy as np


def make_video(path: Path, frames: int = 60, width: int = 640, height: int = 360):
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 20.0,
                             (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not create synthetic demo: {path}")
    try:
        for t in range(frames):
            image = np.full((height, width, 3), (30, 25, 22), dtype=np.uint8)
            x = 40 + round(t * (width - 160) / max(1, frames - 1))
            cv2.rectangle(image, (x, 100), (x + 64, 175), (40, 190, 210), -1)
            y = 180 - round(45 * np.sin(t / 9))
            cv2.circle(image, (width - x, y), 35, (180, 100, 50), -1)
            cv2.putText(image, "SYNTHETIC INPUT - NOT AN ACCURACY BENCHMARK",
                        (18, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.56,
                        (230, 230, 230), 1, cv2.LINE_AA)
            writer.write(image)
    finally:
        writer.release()
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate original synthetic MP4")
    parser.add_argument("--output", type=Path, default=Path("data/input/sample_video.mp4"))
    args = parser.parse_args()
    print(f"Created {make_video(args.output)}")
