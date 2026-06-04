import cv2

from detect import Detector
from tracker import Tracker

detector = Detector()
tracker = Tracker()

VIDEO_PATH = r"Store 1-20260602T101818Z-3-001ec38db8\Store 1\CAM 3 - entry.mp4"

cap = cv2.VideoCapture(VIDEO_PATH)

print("Video Opened:", cap.isOpened())

while True:

    ret, frame = cap.read()

    if not ret:
        break

    detections = detector.detect(
        frame
    )

    tracks = tracker.update(
        detections,
        frame
    )

    for track in tracks:

        x1,y1,x2,y2 = track["bbox"]

        track_id = track["track_id"]

        cv2.rectangle(
            frame,
            (x1,y1),
            (x2,y2),
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"ID {track_id}",
            (x1,y1-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2
        )

    cv2.imshow(
        "StrongSORT Tracking",
        frame
    )

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()