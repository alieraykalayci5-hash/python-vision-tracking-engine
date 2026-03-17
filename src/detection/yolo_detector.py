from ultralytics import YOLO


class YOLODetector:
    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.3):
        self.model = YOLO(model_name)
        self.conf_threshold = conf_threshold

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        detections = []

        if results.boxes is None:
            return detections

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < self.conf_threshold:
                continue

            cls = int(box.cls[0])
            xyxy = box.xyxy[0].tolist()
            x1, y1, x2, y2 = map(int, xyxy)

            detections.append(
                {
                    "bbox": (x1, y1, x2, y2),
                    "confidence": conf,
                    "class_id": cls,
                }
            )

        return detections