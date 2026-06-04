import uuid
import json
from datetime import datetime, timezone


class EventBuilder:

    def __init__(self, output_file):

        self.output_file = output_file

    def build_event(
        self,
        store_id,
        camera_id,
        visitor_id,
        event_type,
        zone_id=None,
        dwell_ms=0,
        is_staff=False,
        confidence=1.0,
        queue_depth=None,
        session_seq=0,
        metadata=None
    ):

        event = {
            "event_id": str(uuid.uuid4()),
            "store_id": store_id,
            "camera_id": camera_id,
            "visitor_id": visitor_id,
            "event_type": event_type,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "zone_id": zone_id,
            "dwell_ms": dwell_ms,
            "is_staff": is_staff,
            "confidence": round(
                float(confidence),
                4
            ),
            "metadata": {
                "queue_depth": queue_depth,
                "session_seq": session_seq
            }
        }

        if metadata:
            event["metadata"].update(
                metadata
            )

        return event

    def save_event(self, event):

        with open(
            self.output_file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                json.dumps(event)
                + "\n"
            )

    def emit(
        self,
        store_id,
        camera_id,
        visitor_id,
        event_type,
        zone_id=None,
        dwell_ms=0,
        is_staff=False,
        confidence=1.0,
        queue_depth=None,
        session_seq=0,
        metadata=None
    ):

        event = self.build_event(
            store_id=store_id,
            camera_id=camera_id,
            visitor_id=visitor_id,
            event_type=event_type,
            zone_id=zone_id,
            dwell_ms=dwell_ms,
            is_staff=is_staff,
            confidence=confidence,
            queue_depth=queue_depth,
            session_seq=session_seq,
            metadata=metadata
        )

        self.save_event(event)

        return event