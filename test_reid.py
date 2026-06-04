import cv2

from detect import Detector
from tracker import Tracker
from reid import ReIDManager

detector = Detector()
tracker = Tracker()
reid = ReIDManager()

VIDEO_PATH = r"Store 1-20260602T101818Z-3-001ec38db8\Store 1\CAM 1 - zone.mp4"

cap = cv2.VideoCapture(VIDEO_PATH)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    detections = detector.detect(frame)

    tracks = tracker.update(
        detections,
        frame
    )

    for track in tracks:

        visitor_id = reid.process_track(
            frame,
            track
        )

        x1,y1,x2,y2 = track["bbox"]

        cv2.rectangle(
            frame,
            (x1,y1),
            (x2,y2),
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            visitor_id,
            (x1,y1-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0,255,0),
            2
        )
    display = cv2.resize(
    frame,
    None,
    fx=0.6,
    fy=0.6
    )
    cv2.imshow(
    "ReID Test",
    display
    )

   

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()