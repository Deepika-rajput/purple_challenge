import pandas as pd
from datetime import datetime, timedelta

from config import (
    PURCHASE_LOOKBACK_MINUTES
)


class POSCorrelator:

    def __init__(self, csv_file):

        self.transactions = pd.read_csv(
            csv_file
        )

        self._prepare()

    def _prepare(self):

        if (
            "timestamp"
            in self.transactions.columns
        ):

            self.transactions[
                "timestamp"
            ] = pd.to_datetime(
                self.transactions[
                    "timestamp"
                ]
            )

            return

        # sample POS file handling

        if (
            "order_date"
            in self.transactions.columns
            and
            "order_time"
            in self.transactions.columns
        ):

            self.transactions[
                "timestamp"
            ] = pd.to_datetime(
                self.transactions[
                    "order_date"
                ].astype(str)
                +
                " "
                +
                self.transactions[
                    "order_time"
                ].astype(str)
            )

    def find_matching_transaction(
        self,
        billing_timestamp,
        store_id
    ):

        start_window = (
            billing_timestamp
        )

        end_window = (
            billing_timestamp
            +
            timedelta(
                minutes=
                PURCHASE_LOOKBACK_MINUTES
            )
        )

        candidates = (
            self.transactions[
                (
                    self.transactions[
                        "timestamp"
                    ]
                    >= start_window
                )
                &
                (
                    self.transactions[
                        "timestamp"
                    ]
                    <= end_window
                )
            ]
        )

        if len(candidates) == 0:
            return None

        return candidates.iloc[0]

    def correlate_purchase(
        self,
        visitor_id,
        billing_timestamp,
        store_id
    ):

        txn = (
            self.find_matching_transaction(
                billing_timestamp,
                store_id
            )
        )

        if txn is None:
            return None

        return {
            "visitor_id":
            visitor_id,

            "transaction_id":
            str(
                txn.get(
                    "transaction_id",
                    txn.get(
                        "order_id",
                        "UNKNOWN"
                    )
                )
            ),

            "transaction_time":
            str(
                txn["timestamp"]
            ),

            "amount":
            float(
                txn.get(
                    "basket_value_inr",
                    txn.get(
                        "total_amount",
                        0
                    )
                )
            )
        }

    def create_purchase_event(
        self,
        visitor_id,
        purchase
    ):

        return {

            "event_type":
            "PURCHASE",

            "visitor_id":
            visitor_id,

            "transaction_id":
            purchase[
                "transaction_id"
            ],

            "amount":
            purchase[
                "amount"
            ],

            "timestamp":
            purchase[
                "transaction_time"
            ]
        }

    def conversion_rate(
        self,
        total_visitors,
        converted_visitors
    ):

        if total_visitors == 0:
            return 0

        return round(
            (
                converted_visitors
                /
                total_visitors
            )
            * 100,
            2
        )

    def total_revenue(self):

        if (
            "total_amount"
            in self.transactions.columns
        ):

            return float(
                self.transactions[
                    "total_amount"
                ].sum()
            )

        if (
            "basket_value_inr"
            in self.transactions.columns
        ):

            return float(
                self.transactions[
                    "basket_value_inr"
                ].sum()
            )

        return 0

    def total_transactions(self):

        return len(
            self.transactions
        )

    def average_basket_value(self):

        if (
            "total_amount"
            in self.transactions.columns
        ):

            return float(
                self.transactions[
                    "total_amount"
                ].mean()
            )

        if (
            "basket_value_inr"
            in self.transactions.columns
        ):

            return float(
                self.transactions[
                    "basket_value_inr"
                ].mean()
            )

        return 0