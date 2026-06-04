import supervision as sv
import numpy as np


class Tracker:

    def __init__(self):

        self.tracker = sv.ByteTrack()

    def update(
        self,
        detections,
        frame
    ):

        if len(detections) == 0:
            return []

        xyxy = []
        confidence = []
        class_id = []

        for det in detections:

            xyxy.append(
                det["bbox"]
            )

            confidence.append(
                det["confidence"]
            )

            class_id.append(
                det["class_id"]
            )

        xyxy = np.array(
            xyxy,
            dtype=np.float32
        )

        confidence = np.array(
            confidence,
            dtype=np.float32
        )

        class_id = np.array(
            class_id,
            dtype=np.int32
        )

        detections_sv = sv.Detections(
            xyxy=xyxy,
            confidence=confidence,
            class_id=class_id
        )

        detections_sv = (
            self.tracker.update_with_detections(
                detections_sv
            )
        )

        tracks = []

        if detections_sv.tracker_id is None:
            return tracks

        for bbox, conf, tid in zip(
            detections_sv.xyxy,
            detections_sv.confidence,
            detections_sv.tracker_id
        ):

            x1, y1, x2, y2 = map(
                int,
                bbox
            )

            tracks.append({
                "track_id": int(tid),
                "bbox": [
                    x1,
                    y1,
                    x2,
                    y2
                ],
                "confidence": float(conf)
            })

        return tracks

    def get_center(
        self,
        bbox
    ):

        x1, y1, x2, y2 = bbox

        return (
            int((x1 + x2) / 2),
            int((y1 + y2) / 2)
        )