import numpy as np
import pandas as pd


np.random.seed(42)

INTERVENTIONS = [
    "RETRY_PAYMENT",
    "SEND_REMINDER",
    "ALTERNATE_PAYMENT",
]


def get_hidden_probabilities(row):
    """
    Generate hidden recovery probabilities for each intervention.

    Undertow will NOT see these probabilities.
    They represent the simulated ground truth.
    """

    probabilities = {
        "RETRY_PAYMENT": 0.45,
        "SEND_REMINDER": 0.40,
        "ALTERNATE_PAYMENT": 0.50,
    }

    # Payment failures are generally good candidates for retry.
    if row["event_type"] == "PAYMENT_FAILED":
        probabilities["RETRY_PAYMENT"] += 0.20

    # Checkout abandonment responds better to reminders.
    if row["event_type"] == "CHECKOUT_ABANDONED":
        probabilities["SEND_REMINDER"] += 0.20

    # Subscription failures benefit from alternate payment methods.
    if row["event_type"] == "SUBSCRIPTION_FAILED":
        probabilities["ALTERNATE_PAYMENT"] += 0.15

    # Overdue invoices respond better to reminders.
    if row["event_type"] == "INVOICE_OVERDUE":
        probabilities["SEND_REMINDER"] += 0.15

    # E42 is deliberately harder to recover through retry.
    if row["error_code"] == "E42":
        probabilities["RETRY_PAYMENT"] -= 0.15
        probabilities["ALTERNATE_PAYMENT"] += 0.10

    # Hidden systemic problem:
    # Bank A + E42 responds poorly to direct payment retries.
    if row["bank"] == "Bank_A" and row["error_code"] == "E42":
        probabilities["RETRY_PAYMENT"] -= 0.20
        probabilities["ALTERNATE_PAYMENT"] += 0.15

    # Keep probabilities between 5% and 90%.
    for intervention in probabilities:
        probabilities[intervention] = np.clip(
            probabilities[intervention],
            0.05,
            0.90,
        )

    return probabilities


def simulate_recovery(df):
    """
    Create hidden ground truth for every event and intervention.
    """

    df = df.copy()

    hidden_probabilities = []

    for _, row in df.iterrows():
        probabilities = get_hidden_probabilities(row)
        hidden_probabilities.append(probabilities)

    for intervention in INTERVENTIONS:

        name = intervention.lower()

        # Store the hidden probability.
        # This is ground truth and will NOT be used as an ML feature.
        df[f"hidden_prob_{name}"] = [
            probabilities[intervention]
            for probabilities in hidden_probabilities
        ]

        # Simulate whether the intervention succeeds.
        random_values = np.random.random(len(df))

        df[f"recovered_{name}"] = (
            random_values < df[f"hidden_prob_{name}"]
        )

        # Amount recovered if the intervention succeeds.
        df[f"amount_recovered_{name}"] = np.where(
            df[f"recovered_{name}"],
            df["amount"],
            0,
        )

    return df


if __name__ == "__main__":

    # Load the original revenue events.
    df = pd.read_csv("data/revenue_events.csv")

    # Generate simulated recovery outcomes.
    df = simulate_recovery(df)

    print("Total events:", len(df))
    print()

    # Display recovery results for each intervention.
    for intervention in INTERVENTIONS:

        name = intervention.lower()

        recovered_count = df[
            f"recovered_{name}"
        ].sum()

        recovered_amount = df[
            f"amount_recovered_{name}"
        ].sum()

        print(intervention)
        print("  Recovered events:", recovered_count)
        print(f"  Amount recovered: ₹{recovered_amount:,.2f}")
        print()

    # Save the complete simulated outcomes.
    output_path = "data/recovery_outcomes.csv"

    df.to_csv(output_path, index=False)

    print(f"Saved outcomes to: {output_path}")