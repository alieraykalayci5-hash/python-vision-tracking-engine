import cv2


class VideoWriter:
    def __init__(self, output_path: str, fps: float, width: int, height: int):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not self.writer.isOpened():
            raise ValueError(f"Could not open video writer: {output_path}")

    def write(self, frame) -> None:
        self.writer.write(frame)

    def release(self) -> None:
        if self.writer is not None:
            self.writer.release()