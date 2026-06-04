import time

from config import (
    QUEUE_TIMEOUT_SECONDS,
    QUEUE_JOIN_THRESHOLD
)


class QueueDetector:

    def __init__(self):

        # visitor_id -> join timestamp
        self.queue_members = {}

        # visitor_id -> purchased
        self.purchased = {}

        # historical stats
        self.completed_wait_times = []

    def join_queue(
        self,
        visitor_id
    ):

        if visitor_id in self.queue_members:
            return None

        self.queue_members[
            visitor_id
        ] = time.time()

        queue_depth = self.get_depth()

        if queue_depth >= \
                QUEUE_JOIN_THRESHOLD:

            return {
                "event_type":
                "BILLING_QUEUE_JOIN",

                "queue_depth":
                queue_depth
            }

        return None

    def leave_queue(
        self,
        visitor_id
    ):

        if visitor_id not in \
                self.queue_members:

            return None

        join_time = (
            self.queue_members[
                visitor_id
            ]
        )

        wait_time = (
            time.time()
            - join_time
        )

        del self.queue_members[
            visitor_id
        ]

        if visitor_id in \
                self.purchased:

            del self.purchased[
                visitor_id
            ]

            self.completed_wait_times.append(
                wait_time
            )

            return {
                "event_type":
                "QUEUE_COMPLETED",

                "wait_time":
                wait_time
            }

        return {
            "event_type":
            "QUEUE_LEFT",

            "wait_time":
            wait_time
        }

    def register_purchase(
        self,
        visitor_id
    ):

        if visitor_id not in \
                self.queue_members:

            return False

        self.purchased[
            visitor_id
        ] = True

        return True

    def detect_abandonments(
        self
    ):

        now = time.time()

        events = []

        abandoned = []

        for visitor_id, join_time in \
                self.queue_members.items():

            wait_time = (
                now - join_time
            )

            purchased = (
                visitor_id
                in self.purchased
            )

            if (
                wait_time >
                QUEUE_TIMEOUT_SECONDS
                and
                not purchased
            ):

                abandoned.append(
                    visitor_id
                )

                events.append(
                    {
                        "event_type":
                        "BILLING_QUEUE_ABANDON",

                        "visitor_id":
                        visitor_id,

                        "wait_time":
                        round(
                            wait_time,
                            2
                        )
                    }
                )

        for visitor_id in abandoned:

            del self.queue_members[
                visitor_id
            ]

        return events

    def get_depth(
        self
    ):

        return len(
            self.queue_members
        )

    def get_average_wait_time(
        self
    ):

        if len(
            self.completed_wait_times
        ) == 0:

            return 0

        return (
            sum(
                self.completed_wait_times
            )
            /
            len(
                self.completed_wait_times
            )
        )

    def get_queue_stats(
        self
    ):

        return {

            "queue_depth":
            self.get_depth(),

            "average_wait_time":
            round(
                self.get_average_wait_time(),
                2
            ),

            "active_members":
            len(
                self.queue_members
            )
        }

    def is_in_queue(
        self,
        visitor_id
    ):

        return (
            visitor_id
            in self.queue_members
        )

    def get_wait_time(
        self,
        visitor_id
    ):

        if visitor_id not in \
                self.queue_members:

            return 0

        return (
            time.time()
            -
            self.queue_members[
                visitor_id
            ]
        )