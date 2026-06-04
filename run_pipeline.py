import cv2
import time

from config import (
    STORE_ID,
    ENTRY_VIDEO,
    OUTPUT_EVENTS,
    ENTRY_LINE_X,
    ZONE_CONFIG,
    POS_FILE,

    ENTRY,
    EXIT,
    REENTRY,
    ZONE_ENTER,
    ZONE_EXIT,
    ZONE_DWELL,
    BILLING_QUEUE_JOIN,
    BILLING_QUEUE_ABANDON
)

from detect import Detector
from tracker import Tracker
from reid import ReIDManager
from zones import ZoneManager
from session_manager import SessionManager
from queue_detector import QueueDetector
from pos_correlator import POSCorrelator
from event_builder import EventBuilder


class StorePipeline:

    def __init__(self):

        self.detector = Detector()

        self.tracker = Tracker()

        self.reid = ReIDManager()

        self.zone_manager = ZoneManager(
            ZONE_CONFIG
        )

        self.sessions = SessionManager()

        self.queue_detector = QueueDetector()

        self.pos = POSCorrelator(
            POS_FILE
        )

        self.events = EventBuilder(
            OUTPUT_EVENTS
        )

        self.previous_positions = {}

    def process_entry_logic(
        self,
        visitor_id,
        cx
    ):

        if visitor_id not in \
                self.previous_positions:

            self.previous_positions[
                visitor_id
            ] = cx

            return

        prev_x = self.previous_positions[
            visitor_id
        ]

        # ENTRY

        if (
            prev_x > ENTRY_LINE_X
            and
            cx < ENTRY_LINE_X
        ):

            event = (
                self.sessions.start_session(
                    visitor_id
                )
            )

            event_type = event["type"]

            self.events.emit(
                store_id=STORE_ID,
                camera_id="CAM3",
                visitor_id=visitor_id,
                event_type=event_type
            )

        # EXIT

        elif (
            prev_x < ENTRY_LINE_X
            and
            cx > ENTRY_LINE_X
        ):

            exit_event = (
                self.sessions.end_session(
                    visitor_id
                )
            )

            if exit_event:

                self.events.emit(
                    store_id=STORE_ID,
                    camera_id="CAM3",
                    visitor_id=visitor_id,
                    event_type=EXIT
                )

        self.previous_positions[
            visitor_id
        ] = cx

    def process_zone_logic(
        self,
        visitor_id,
        cx,
        cy
    ):

        zone = self.zone_manager.get_zone(
            cx,
            cy
        )

        if zone is None:
            return

        events = self.zone_manager.update(
            visitor_id,
            zone
        )

        for e in events:

            self.sessions.add_zone(
                visitor_id,
                zone
            )

            event_type = e["type"]

            dwell_ms = int(
                e.get(
                    "dwell",
                    0
                ) * 1000
            )

            self.events.emit(
                store_id=STORE_ID,
                camera_id="ZONE_CAM",
                visitor_id=visitor_id,
                event_type=event_type,
                zone_id=zone,
                dwell_ms=dwell_ms
            )

    def process_queue_logic(
        self,
        visitor_id,
        zone
    ):

        if zone != "BILLING":
            return

        queue_event = (
            self.queue_detector.join_queue(
                visitor_id
            )
        )

        if queue_event:

            self.sessions.join_billing(
                visitor_id
            )

            self.events.emit(
                store_id=STORE_ID,
                camera_id="CAM5",
                visitor_id=visitor_id,
                event_type=
                BILLING_QUEUE_JOIN,
                zone_id="BILLING",
                queue_depth=
                queue_event[
                    "queue_depth"
                ]
            )

    def process_frame(
        self,
        frame
    ):

        detections = (
            self.detector.detect(
                frame
            )
        )

        tracks = self.tracker.update(
            detections,
            frame
        )

        for track in tracks:

            bbox = track["bbox"]

            visitor_id = (
                self.reid.process_track(
                    frame,
                    track
                )
            )

            x1,y1,x2,y2 = bbox

            cx = int(
                (x1+x2)/2
            )

            cy = int(
                (y1+y2)/2
            )

            self.process_entry_logic(
                visitor_id,
                cx
            )

            self.process_zone_logic(
                visitor_id,
                cx,
                cy
            )

            zone = (
                self.zone_manager.get_zone(
                    cx,
                    cy
                )
            )

            if zone:

                self.process_queue_logic(
                    visitor_id,
                    zone
                )

        # abandonment checks

        abandonments = (
            self.queue_detector
            .detect_abandonments()
        )

        for abandon in abandonments:

            self.events.emit(
                store_id=STORE_ID,
                camera_id="CAM5",
                visitor_id=
                abandon[
                    "visitor_id"
                ],
                event_type=
                BILLING_QUEUE_ABANDON
            )

    def run(
        self,
        video_path
    ):

        cap = cv2.VideoCapture(
            str(video_path)
        )

        frame_count = 0

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frame_count += 1

            self.process_frame(
                frame
            )

            if frame_count % 100 == 0:

                print(
                    f"Processed "
                    f"{frame_count} frames"
                )

        cap.release()

        print(
            "Pipeline completed"
        )

        print(
            "Events saved to:",
            OUTPUT_EVENTS
        )


if __name__ == "__main__":

    pipeline = StorePipeline()

    pipeline.run(
        ENTRY_VIDEO
    )