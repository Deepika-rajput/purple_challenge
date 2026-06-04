import cv2
import numpy as np
from ultralytics import RTDETR

from config import (
    RTDETR_MODEL,
    MIN_CONFIDENCE
)


class Detector:

    def __init__(self):

        print(
            f"[INFO] Loading RT-DETR model: "
            f"{RTDETR_MODEL}"
        )

        self.model = RTDETR(
            RTDETR_MODEL
        )

    def detect(self, frame):

        results = self.model.predict(
            source=frame,
            conf=MIN_CONFIDENCE,
            verbose=False
        )

        detections = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                cls = int(
                    box.cls.item()
                )

                # COCO class 0 = person
                if cls != 0:
                    continue

                conf = float(
                    box.conf.item()
                )

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                detections.append({
                    "bbox": [
                        x1,
                        y1,
                        x2,
                        y2
                    ],
                    "confidence": conf,
                    "class_id": cls
                })

        return detections

    def draw_detections(
        self,
        frame,
        detections
    ):

        output = frame.copy()

        for det in detections:

            x1, y1, x2, y2 = det["bbox"]

            conf = det["confidence"]

            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                output,
                f"{conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return output


if __name__ == "__main__":

    detector = Detector()

    VIDEO_PATH = r"Store 1-20260602T101818Z-3-001ec38db8\Store 1\CAM 3 - entry.mp4"
    import os
    print("Exists:", os.path.exists(VIDEO_PATH))

    cap = cv2.VideoCapture(VIDEO_PATH)

    print("Video Path:", VIDEO_PATH)
    print("Video Opened:", cap.isOpened())

    if not cap.isOpened():
        print("ERROR: Cannot open video.")
        exit()

    while True:

        ret, frame = cap.read()

        if not ret:
            print("End of video reached.")
            break

        detections = detector.detect(frame)

        frame = detector.draw_detections(
            frame,
            detections
        )

        cv2.imshow(
            "RT-DETR Detection",
            frame
        )

        key = cv2.waitKey(1)

        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()