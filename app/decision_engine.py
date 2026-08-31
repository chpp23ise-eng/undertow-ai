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


def rank_interventions(model, event):
    """
    Predict the recovery probability for every intervention
    and rank them by expected money recovered.
    """

    rows = []

    for intervention in INTERVENTIONS:
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

    probabilities = model.predict_proba(candidates)[:, 1]

    candidates["recovery_probability"] = probabilities

    candidates["expected_recovery"] = (
        candidates["amount"]
        * candidates["recovery_probability"]
    )

    candidates = candidates.sort_values(
        "expected_recovery",
        ascending=False,
    ).reset_index(drop=True)

    return candidates


def make_decision(model, event):
    """Choose the intervention with the highest expected recovery."""

    ranked = rank_interventions(model, event)

    best = ranked.iloc[0]

    return {
        "event_id": event["event_id"],
        "amount": event["amount"],
        "recommended_action": best["intervention"],
        "recovery_probability": best["recovery_probability"],
        "expected_recovery": best["expected_recovery"],
        "ranked_options": ranked,
    }


if __name__ == "__main__":

    # Load the trained model.
    model = load_model()

    # Load our event data.
    df = pd.read_csv("data/revenue_events.csv")

    # Pick one event to demonstrate the decision engine.
    event = df.iloc[0].to_dict()

    decision = make_decision(model, event)

    print("UNDERTOW RECOVERY DECISION")
    print("==========================")
    print()

    print(f"Event: {decision['event_id']}")
    print(f"Amount: ₹{decision['amount']:,.2f}")
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
    print("--------------------------")

    display_columns = [
        "intervention",
        "recovery_probability",
        "expected_recovery",
    ]

    print(
        decision["ranked_options"][display_columns]
        .to_string(index=False)
    )