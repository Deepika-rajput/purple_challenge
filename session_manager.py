import time
from collections import defaultdict

from config import (
    ENTRY,
    EXIT,
    REENTRY
)


class SessionManager:

    def __init__(self):

        # active sessions
        self.active_sessions = {}

        # completed sessions
        self.completed_sessions = []

        # visitor last exit
        self.last_exit_time = {}

        # session sequence
        self.session_sequence = defaultdict(int)

        # funnel tracking
        self.funnel_stage = {}

    def start_session(
        self,
        visitor_id
    ):

        now = time.time()

        is_reentry = (
            visitor_id
            in self.last_exit_time
        )

        self.session_sequence[
            visitor_id
        ] += 1

        session_seq = (
            self.session_sequence[
                visitor_id
            ]
        )

        self.active_sessions[
            visitor_id
        ] = {

            "visitor_id":
            visitor_id,

            "session_seq":
            session_seq,

            "entry_time":
            now,

            "exit_time":
            None,

            "duration":
            0,

            "events":
            [],

            "zones":
            set(),

            "purchased":
            False
        }

        self.funnel_stage[
            visitor_id
        ] = "ENTRY"

        if is_reentry:

            return {
                "type":
                REENTRY,

                "session_seq":
                session_seq
            }

        return {
            "type":
            ENTRY,

            "session_seq":
            session_seq
        }

    def end_session(
        self,
        visitor_id
    ):

        if visitor_id not in \
                self.active_sessions:

            return None

        now = time.time()

        session = (
            self.active_sessions[
                visitor_id
            ]
        )

        session[
            "exit_time"
        ] = now

        session[
            "duration"
        ] = (
            now
            -
            session[
                "entry_time"
            ]
        )

        self.last_exit_time[
            visitor_id
        ] = now

        self.completed_sessions.append(
            session
        )

        del self.active_sessions[
            visitor_id
        ]

        if visitor_id in \
                self.funnel_stage:

            del self.funnel_stage[
                visitor_id
            ]

        return {
            "type":
            EXIT,

            "duration":
            session[
                "duration"
            ]
        }

    def add_event(
        self,
        visitor_id,
        event
    ):

        if visitor_id not in \
                self.active_sessions:

            return

        self.active_sessions[
            visitor_id
        ]["events"].append(
            event
        )

    def add_zone(
        self,
        visitor_id,
        zone
    ):

        if visitor_id not in \
                self.active_sessions:

            return

        self.active_sessions[
            visitor_id
        ]["zones"].add(
            zone
        )

        self.funnel_stage[
            visitor_id
        ] = "ZONE"

    def join_billing(
        self,
        visitor_id
    ):

        if visitor_id not in \
                self.active_sessions:

            return

        self.funnel_stage[
            visitor_id
        ] = "BILLING"

    def purchase(
        self,
        visitor_id
    ):

        if visitor_id not in \
                self.active_sessions:

            return

        self.active_sessions[
            visitor_id
        ]["purchased"] = True

        self.funnel_stage[
            visitor_id
        ] = "PURCHASE"

    def get_session_seq(
        self,
        visitor_id
    ):

        if visitor_id not in \
                self.active_sessions:

            return 0

        return (
            self.active_sessions[
                visitor_id
            ]["session_seq"]
        )

    def get_active_count(
        self
    ):

        return len(
            self.active_sessions
        )

    def get_funnel_stats(
        self
    ):

        entry = 0
        zone = 0
        billing = 0
        purchase = 0

        sessions = (
            self.completed_sessions
            +
            list(
                self.active_sessions.values()
            )
        )

        for s in sessions:

            entry += 1

            if len(
                s["zones"]
            ) > 0:

                zone += 1

            billing_events = [

                e
                for e
                in s["events"]

                if e.get(
                    "event_type"
                )
                ==
                "BILLING_QUEUE_JOIN"
            ]

            if len(
                billing_events
            ) > 0:

                billing += 1

            if s["purchased"]:

                purchase += 1

        return {

            "entry":
            entry,

            "zone":
            zone,

            "billing":
            billing,

            "purchase":
            purchase
        }

    def get_session(
        self,
        visitor_id
    ):

        return (
            self.active_sessions.get(
                visitor_id
            )
        )

    def get_avg_session_duration(
        self
    ):

        if len(
            self.completed_sessions
        ) == 0:

            return 0

        total = sum(
            s["duration"]
            for s
            in self.completed_sessions
        )

        return (
            total
            /
            len(
                self.completed_sessions
            )
        )