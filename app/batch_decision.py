import joblib
import pandas as pd


MODEL_PATH = "models/recovery_model.joblib"
EVENTS_PATH = "data/revenue_events.csv"
OUTPUT_PATH = "data/decisions.csv"

INTERVENTIONS = [
    "RETRY_PAYMENT",
    "SEND_REMINDER",
    "ALTERNATE_PAYMENT",
]


def load_model():
    return joblib.load(MODEL_PATH)


def predict_interventions(model, events):
    """Predict recovery probability for every event/action combination."""

    rows = []

    for _, event in events.iterrows():

        for intervention in INTERVENTIONS:

            rows.append(
                {
                    "event_id": event["event_id"],
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

    candidates["recovery_probability"] = (
        model.predict_proba(candidates)[:, 1]
    )

    candidates["expected_recovery"] = (
        candidates["amount"]
        * candidates["recovery_probability"]
    )

    return candidates


def select_best_actions(candidates):
    """Select the action with the highest expected recovery per event."""

    best_indices = (
        candidates
        .groupby("event_id")["expected_recovery"]
        .idxmax()
    )

    decisions = candidates.loc[best_indices].copy()

    decisions = decisions.sort_values(
        "expected_recovery",
        ascending=False,
    ).reset_index(drop=True)

    return decisions


def main():

    print("Loading model...")
    model = load_model()

    print("Loading events...")
    events = pd.read_csv(EVENTS_PATH)

    print(f"Events: {len(events)}")
    print()

    print("Evaluating interventions...")

    candidates = predict_interventions(
        model,
        events,
    )

    decisions = select_best_actions(
        candidates,
    )

    decisions.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("Batch decisions created.")
    print(f"Decisions: {len(decisions)}")
    print()

    print("Total expected recovery:")
    print(
        f"₹{decisions['expected_recovery'].sum():,.2f}"
    )

    print()

    print("Recommended actions:")

    print(
        decisions["intervention"]
        .value_counts()
    )

    print()
    print("Top 10 opportunities:")
    print()

    print(
        decisions[
            [
                "event_id",
                "amount",
                "event_type",
                "bank",
                "error_code",
                "intervention",
                "recovery_probability",
                "expected_recovery",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print()
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()