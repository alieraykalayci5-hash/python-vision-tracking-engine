import cv2


class VideoReader:
    def __init__(self, source):
        self.source = source
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video source: {source}")

    def read(self):
        return self.cap.read()

    def get_width(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    def get_height(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_fps(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        return fps if fps and fps > 0 else 30.0

    def release(self):
        if self.cap is not None:
            self.cap.release()
