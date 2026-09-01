import pandas as pd


# Use the same held-out outcomes used by the experiment.
OUTCOMES_PATH = "data/experiment_test_outcomes.csv"


INTERVENTION_COLUMNS = {
    "RETRY_PAYMENT": "amount_recovered_retry_payment",
    "SEND_REMINDER": "amount_recovered_send_reminder",
    "ALTERNATE_PAYMENT": "amount_recovered_alternate_payment",
}


def load_outcomes():
    """Load the experiment's ground-truth recovery outcomes."""

    return pd.read_csv(
        OUTCOMES_PATH
    )


def execute_recovery(
    outcomes,
    event_id,
    action,
):
    """
    Look up the simulated outcome for an intervention.

    The simulated recovery amount is bounded by the
    original transaction amount.
    """

    if action not in INTERVENTION_COLUMNS:

        return {
            "event_id": event_id,
            "action": action,
            "status": "FAILED",
            "amount_recovered": 0.0,
            "message": "Unknown recovery action.",
        }


    matching_rows = outcomes[
        outcomes["event_id"] == event_id
    ]


    if matching_rows.empty:

        return {
            "event_id": event_id,
            "action": action,
            "status": "FAILED",
            "amount_recovered": 0.0,
            "message": "Event not found.",
        }


    row = matching_rows.iloc[0]


    # -----------------------------------------------------
    # Original transaction amount
    # -----------------------------------------------------

    if "amount" in row.index:

        original_amount = float(
            row["amount"]
        )

    else:

        original_amount = None


    # -----------------------------------------------------
    # Ground-truth recovery
    # -----------------------------------------------------

    amount_recovered = float(
        row[
            INTERVENTION_COLUMNS[action]
        ]
    )


    # -----------------------------------------------------
    # Safety invariant:
    # recovery cannot exceed transaction amount.
    # -----------------------------------------------------

    if original_amount is not None:

        amount_recovered = min(
            max(
                amount_recovered,
                0.0,
            ),
            original_amount,
        )

    else:

        amount_recovered = max(
            amount_recovered,
            0.0,
        )


    # -----------------------------------------------------
    # Determine outcome
    # -----------------------------------------------------

    if amount_recovered > 0:

        status = "RECOVERED"

        message = (
            "Recovery succeeded."
        )

    else:

        status = "NOT_RECOVERED"

        message = (
            "Recovery attempt did not "
            "recover revenue."
        )


    return {
        "event_id": event_id,
        "action": action,
        "status": status,
        "amount_recovered": amount_recovered,
        "message": message,
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    outcomes = load_outcomes()


    result = execute_recovery(
        outcomes=outcomes,
        event_id="E00005",
        action="SEND_REMINDER",
    )


    print(
        "UNDERTOW RECOVERY SERVICE"
    )

    print(
        "========================="
    )

    print()

    print(
        f"Event: "
        f"{result['event_id']}"
    )

    print(
        f"Action: "
        f"{result['action']}"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    print(
        f"Amount recovered: "
        f"₹{result['amount_recovered']:,.2f}"
    )

    print(
        f"Message: "
        f"{result['message']}"
    )