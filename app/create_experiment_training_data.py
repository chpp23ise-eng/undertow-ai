import pandas as pd


INTERVENTIONS = {
    "RETRY_PAYMENT": "recovered_retry_payment",
    "SEND_REMINDER": "recovered_send_reminder",
    "ALTERNATE_PAYMENT": "recovered_alternate_payment",
}


INPUT_PATH = "data/experiment_train_outcomes.csv"
OUTPUT_PATH = "data/experiment_training_data.csv"


def create_training_data(df):
    """Create one ML row for every event/intervention pair."""

    rows = []

    for _, event in df.iterrows():

        for intervention, outcome_column in INTERVENTIONS.items():

            rows.append(
                {
                    "event_id": event["event_id"],
                    "customer_id": event["customer_id"],
                    "amount": event["amount"],
                    "event_type": event["event_type"],
                    "bank": event["bank"],
                    "error_code": event["error_code"],
                    "product_id": event["product_id"],
                    "payment_method": event["payment_method"],
                    "intervention": intervention,
                    "recovered": int(event[outcome_column]),
                }
            )

    return pd.DataFrame(rows)


def main():

    print("Loading experiment training outcomes...")

    df = pd.read_csv(INPUT_PATH)

    print(f"Events: {len(df)}")
    print()

    training_df = create_training_data(df)

    training_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("Experiment training dataset created.")
    print(f"Rows: {len(training_df)}")
    print(f"Saved to: {OUTPUT_PATH}")
    print()

    print("Recovery rate by intervention:")

    print(
        training_df
        .groupby("intervention")["recovered"]
        .mean()
        .sort_values(ascending=False)
    )


if __name__ == "__main__":
    main()