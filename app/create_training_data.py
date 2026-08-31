import pandas as pd


INTERVENTIONS = {
    "RETRY_PAYMENT": "recovered_retry_payment",
    "SEND_REMINDER": "recovered_send_reminder",
    "ALTERNATE_PAYMENT": "recovered_alternate_payment",
}


def create_training_data(df):
    """
    Convert each event into one row per possible intervention.

    Example:

    Event E001
        -> RETRY_PAYMENT
        -> SEND_REMINDER
        -> ALTERNATE_PAYMENT
    """

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


if __name__ == "__main__":

    # Load simulated recovery outcomes.
    df = pd.read_csv("data/recovery_outcomes.csv")

    # Convert them into ML training examples.
    training_df = create_training_data(df)

    # Save the training dataset.
    output_path = "data/training_data.csv"

    training_df.to_csv(output_path, index=False)

    print("Training dataset created.")
    print(f"Rows: {len(training_df)}")
    print()

    print("Columns:")
    print(list(training_df.columns))
    print()

    print("Recovery rate by intervention:")

    recovery_rates = (
        training_df
        .groupby("intervention")["recovered"]
        .mean()
        .sort_values(ascending=False)
    )

    print(recovery_rates)