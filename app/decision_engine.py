import joblib
import pandas as pd


MODEL_PATH = "models/recovery_model.joblib"

INTERVENTIONS = [
    "RETRY_PAYMENT",
    "SEND_REMINDER",
    "ALTERNATE_PAYMENT",
]


def load_model():
    """Load the trained recovery model."""
    return joblib.load(MODEL_PATH)


def rank_interventions(
    model,
    event,
    excluded_interventions=None,
):
    """
    Predict recovery probability for every available
    intervention and rank them by expected money recovered.

    Interventions that have already been attempted can
    be excluded.
    """

    if excluded_interventions is None:
        excluded_interventions = set()
    else:
        excluded_interventions = set(
            excluded_interventions
        )

    available_interventions = [
        intervention
        for intervention in INTERVENTIONS
        if intervention not in excluded_interventions
    ]

    # No interventions remain.
    if not available_interventions:
        return pd.DataFrame(
            columns=[
                "amount",
                "event_type",
                "bank",
                "error_code",
                "product_id",
                "payment_method",
                "intervention",
                "recovery_probability",
                "expected_recovery",
            ]
        )

    rows = []

    for intervention in available_interventions:

        rows.append(
            {
                "amount": event["amount"],
                "event_type": event["event_type"],
                "bank": event["bank"],
                "error_code": event["error_code"],
                "product_id": event["product_id"],
                "payment_method": event["payment_method"],
                "intervention": intervention,
            }
        )

    candidates = pd.DataFrame(rows)

    probabilities = model.predict_proba(
        candidates
    )[:, 1]

    candidates["recovery_probability"] = (
        probabilities
    )

    candidates["expected_recovery"] = (
        candidates["amount"]
        * candidates["recovery_probability"]
    )

    candidates = candidates.sort_values(
        "expected_recovery",
        ascending=False,
    ).reset_index(drop=True)

    return candidates


def make_decision(
    model,
    event,
    excluded_interventions=None,
):
    """
    Choose the available intervention with the
    highest expected recovery.
    """

    ranked = rank_interventions(
        model=model,
        event=event,
        excluded_interventions=excluded_interventions,
    )

    # No actions remain.
    if ranked.empty:

        return {
            "event_id": event["event_id"],
            "amount": event["amount"],
            "recommended_action": None,
            "recovery_probability": 0.0,
            "expected_recovery": 0.0,
            "ranked_options": ranked,
        }

    best = ranked.iloc[0]

    return {
        "event_id": event["event_id"],
        "amount": event["amount"],
        "recommended_action": best[
            "intervention"
        ],
        "recovery_probability": best[
            "recovery_probability"
        ],
        "expected_recovery": best[
            "expected_recovery"
        ],
        "ranked_options": ranked,
    }


if __name__ == "__main__":

    model = load_model()

    df = pd.read_csv(
        "data/revenue_events.csv"
    )

    event = df.iloc[0].to_dict()

    decision = make_decision(
        model,
        event,
    )

    print(
        "UNDERTOW RECOVERY DECISION"
    )

    print(
        "=========================="
    )

    print()

    print(
        f"Event: {decision['event_id']}"
    )

    print(
        f"Amount: ₹{decision['amount']:,.2f}"
    )

    print()

    print(
        f"Recommended action: "
        f"{decision['recommended_action']}"
    )

    print(
        f"Predicted recovery probability: "
        f"{decision['recovery_probability']:.2%}"
    )

    print(
        f"Expected recovery: "
        f"₹{decision['expected_recovery']:,.2f}"
    )

    print()

    print("All intervention options:")

    print(
        "--------------------------"
    )

    display_columns = [
        "intervention",
        "recovery_probability",
        "expected_recovery",
    ]

    print(
        decision["ranked_options"][
            display_columns
        ].to_string(index=False)
    )