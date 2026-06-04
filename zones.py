import json
import time

from shapely.geometry import Point
from shapely.geometry import Polygon

from config import (
    DWELL_THRESHOLD_SECONDS,
    DWELL_REPEAT_SECONDS
)


class ZoneManager:

    def __init__(self, zone_file):

        with open(zone_file, "r") as f:
            self.zone_config = json.load(f)

        self.polygons = {}

        for zone_name, coords in self.zone_config.items():

            self.polygons[zone_name] = Polygon(
                coords
            )

        # visitor -> zone
        self.current_zone = {}

        # visitor -> entry time
        self.zone_entry_time = {}

        # visitor -> last dwell emit
        self.last_dwell_emit = {}

        # heatmap counts
        self.zone_visit_count = {}

        # dwell totals
        self.zone_dwell_total = {}

    def get_zone(
        self,
        x,
        y
    ):

        point = Point(x, y)

        for zone_name, polygon in \
            self.polygons.items():

            if polygon.contains(point):

                return zone_name

        return None

    def update(
        self,
        visitor_id,
        zone_name,
        timestamp=None
    ):

        if timestamp is None:
            timestamp = time.time()

        events = []

        previous_zone = (
            self.current_zone.get(
                visitor_id
            )
        )

        # ----------------------------------
        # First zone visit
        # ----------------------------------

        if previous_zone is None:

            self.current_zone[
                visitor_id
            ] = zone_name

            self.zone_entry_time[
                visitor_id
            ] = timestamp

            self.last_dwell_emit[
                visitor_id
            ] = timestamp

            self.zone_visit_count[
                zone_name
            ] = (
                self.zone_visit_count.get(
                    zone_name,
                    0
                ) + 1
            )

            events.append(
                {
                    "type":
                    "ZONE_ENTER",

                    "zone":
                    zone_name
                }
            )

            return events

        # ----------------------------------
        # Zone changed
        # ----------------------------------

        if previous_zone != zone_name:

            dwell_time = (
                timestamp
                - self.zone_entry_time[
                    visitor_id
                ]
            )

            self.zone_dwell_total[
                previous_zone
            ] = (
                self.zone_dwell_total.get(
                    previous_zone,
                    0
                )
                + dwell_time
            )

            events.append(
                {
                    "type":
                    "ZONE_EXIT",

                    "zone":
                    previous_zone,

                    "dwell":
                    dwell_time
                }
            )

            self.current_zone[
                visitor_id
            ] = zone_name

            self.zone_entry_time[
                visitor_id
            ] = timestamp

            self.last_dwell_emit[
                visitor_id
            ] = timestamp

            self.zone_visit_count[
                zone_name
            ] = (
                self.zone_visit_count.get(
                    zone_name,
                    0
                ) + 1
            )

            events.append(
                {
                    "type":
                    "ZONE_ENTER",

                    "zone":
                    zone_name
                }
            )

            return events

        # ----------------------------------
        # Dwell event
        # ----------------------------------

        time_in_zone = (
            timestamp
            - self.zone_entry_time[
                visitor_id
            ]
        )

        last_emit = (
            self.last_dwell_emit[
                visitor_id
            ]
        )

        if (
            time_in_zone
            >= DWELL_THRESHOLD_SECONDS
            and
            timestamp - last_emit
            >= DWELL_REPEAT_SECONDS
        ):

            self.last_dwell_emit[
                visitor_id
            ] = timestamp

            events.append(
                {
                    "type":
                    "ZONE_DWELL",

                    "zone":
                    zone_name,

                    "dwell":
                    time_in_zone
                }
            )

        return events

    def force_exit(
        self,
        visitor_id,
        timestamp=None
    ):

        if timestamp is None:
            timestamp = time.time()

        if visitor_id not in \
                self.current_zone:

            return None

        zone = self.current_zone[
            visitor_id
        ]

        dwell_time = (
            timestamp
            - self.zone_entry_time[
                visitor_id
            ]
        )

        self.zone_dwell_total[
            zone
        ] = (
            self.zone_dwell_total.get(
                zone,
                0
            )
            + dwell_time
        )

        del self.current_zone[
            visitor_id
        ]

        del self.zone_entry_time[
            visitor_id
        ]

        del self.last_dwell_emit[
            visitor_id
        ]

        return {
            "type":
            "ZONE_EXIT",

            "zone":
            zone,

            "dwell":
            dwell_time
        }

    def get_heatmap_data(self):

        output = {}

        for zone in \
                self.zone_visit_count:

            visits = (
                self.zone_visit_count[
                    zone
                ]
            )

            total_dwell = (
                self.zone_dwell_total.get(
                    zone,
                    0
                )
            )

            avg_dwell = 0

            if visits > 0:

                avg_dwell = (
                    total_dwell
                    / visits
                )

            output[zone] = {

                "visits":
                visits,

                "avg_dwell":
                round(
                    avg_dwell,
                    2
                )
            }

        return output