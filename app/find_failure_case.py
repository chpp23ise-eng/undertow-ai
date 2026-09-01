import pandas as pd

from decision_engine import load_model, make_decision


EVENTS_PATH = "data/experiment_test_events.csv"
OUTCOMES_PATH = "data/experiment_test_outcomes.csv"


def get_actual_recovery(row, action):
    """Get the ground-truth recovery for an intervention."""

    columns = {
        "RETRY_PAYMENT":
            "amount_recovered_retry_payment",

        "SEND_REMINDER":
            "amount_recovered_send_reminder",

        "ALTERNATE_PAYMENT":
            "amount_recovered_alternate_payment",
    }

    return float(
        row[columns[action]]
    )


def find_failure_case():

    print(
        "Searching held-out experiment "
        "data for a multi-attempt case..."
    )

    events = pd.read_csv(
        EVENTS_PATH
    )

    outcomes = pd.read_csv(
        OUTCOMES_PATH
    )

    model = load_model()

    merged = events.merge(
        outcomes,
        on="event_id",
        how="inner",
        suffixes=(
            "",
            "_outcome",
        ),
    )

    for _, row in merged.iterrows():

        event = {
            "event_id":
                row["event_id"],

            "customer_id":
                row["customer_id"],

            "amount":
                row["amount"],

            "event_type":
                row["event_type"],

            "bank":
                row["bank"],

            "error_code":
                row["error_code"],

            "product_id":
                row["product_id"],

            "payment_method":
                row["payment_method"],
        }

        decision = make_decision(
            model,
            event,
        )

        ranked = (
            decision[
                "ranked_options"
            ].copy()
        )

        best_action = (
            ranked.iloc[0][
                "intervention"
            ]
        )

        best_probability = float(
            ranked.iloc[0][
                "recovery_probability"
            ]
        )

        best_expected = float(
            ranked.iloc[0][
                "expected_recovery"
            ]
        )

        best_actual = (
            get_actual_recovery(
                row,
                best_action,
            )
        )

        # The best predicted action must fail.
        if best_actual > 0:
            continue

        # Look for another intervention
        # that actually succeeds.
        for _, alternative in (
            ranked.iloc[1:].iterrows()
        ):

            alternative_action = (
                alternative[
                    "intervention"
                ]
            )

            alternative_actual = (
                get_actual_recovery(
                    row,
                    alternative_action,
                )
            )

            if alternative_actual > 0:

                print()
                print(
                    "FOUND FAILURE CASE"
                )

                print(
                    "==================="
                )

                print()

                print(
                    f"Event: "
                    f"{event['event_id']}"
                )

                print(
                    f"Amount: "
                    f"₹{event['amount']:,.2f}"
                )

                print(
                    f"Event type: "
                    f"{event['event_type']}"
                )

                print(
                    f"Bank: "
                    f"{event['bank']}"
                )

                print(
                    f"Error: "
                    f"{event['error_code']}"
                )

                print()

                print(
                    f"Best action: "
                    f"{best_action}"
                )

                print(
                    f"Predicted probability: "
                    f"{best_probability:.2%}"
                )

                print(
                    f"Expected recovery: "
                    f"₹{best_expected:,.2f}"
                )

                print(
                    f"Actual result: "
                    f"NOT_RECOVERED"
                )

                print(
                    f"Actual recovered: "
                    f"₹{best_actual:,.2f}"
                )

                print()

                print(
                    f"Successful alternative: "
                    f"{alternative_action}"
                )

                print(
                    f"Alternative actual recovery: "
                    f"₹{alternative_actual:,.2f}"
                )

                print()

                print(
                    "This event can demonstrate "
                    "multi-attempt recovery."
                )

                return event

    print()
    print(
        "No suitable multi-attempt failure "
        "case was found."
    )

    return None


if __name__ == "__main__":

    find_failure_case()