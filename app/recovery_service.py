import pandas as pd


OUTCOMES_PATH = "data/recovery_outcomes.csv"

INTERVENTION_COLUMNS = {
    "RETRY_PAYMENT": "amount_recovered_retry_payment",
    "SEND_REMINDER": "amount_recovered_send_reminder",
    "ALTERNATE_PAYMENT": "amount_recovered_alternate_payment",
}


def load_outcomes():
    """Load the simulator's ground-truth outcomes."""
    return pd.read_csv(OUTCOMES_PATH)


def execute_recovery(outcomes, event_id, action):
    """
    Look up what actually happened when this intervention
    was applied to this event in our simulated environment.

    In production, this function would call a real payment/
    messaging service instead.
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

    amount_recovered = float(
        row[INTERVENTION_COLUMNS[action]]
    )

    if amount_recovered > 0:
        status = "RECOVERED"
        message = "Recovery succeeded."
    else:
        status = "NOT_RECOVERED"
        message = "Recovery attempt did not recover revenue."

    return {
        "event_id": event_id,
        "action": action,
        "status": status,
        "amount_recovered": amount_recovered,
        "message": message,
    }


if __name__ == "__main__":

    outcomes = load_outcomes()

    result = execute_recovery(
        outcomes=outcomes,
        event_id="E00001",
        action="ALTERNATE_PAYMENT",
    )

    print("UNDERTOW RECOVERY SERVICE")
    print("=========================")
    print()

    print(f"Event: {result['event_id']}")
    print(f"Action: {result['action']}")
    print(f"Status: {result['status']}")
    print(f"Amount recovered: ₹{result['amount_recovered']:,.2f}")
    print(f"Message: {result['message']}")