import numpy as np
import pandas as pd


INTERVENTIONS = [
    "RETRY_PAYMENT",
    "SEND_REMINDER",
    "ALTERNATE_PAYMENT",
]


def get_hidden_probabilities(row):
    """
    Generate hidden recovery probabilities.

    Undertow does NOT see these probabilities.
    They represent simulated ground truth.
    """

    probabilities = {
        "RETRY_PAYMENT": 0.45,
        "SEND_REMINDER": 0.40,
        "ALTERNATE_PAYMENT": 0.50,
    }

    if row["event_type"] == "PAYMENT_FAILED":
        probabilities["RETRY_PAYMENT"] += 0.20

    if row["event_type"] == "CHECKOUT_ABANDONED":
        probabilities["SEND_REMINDER"] += 0.20

    if row["event_type"] == "SUBSCRIPTION_FAILED":
        probabilities["ALTERNATE_PAYMENT"] += 0.15

    if row["event_type"] == "INVOICE_OVERDUE":
        probabilities["SEND_REMINDER"] += 0.15

    if row["error_code"] == "E42":
        probabilities["RETRY_PAYMENT"] -= 0.15
        probabilities["ALTERNATE_PAYMENT"] += 0.10

    if (
        row["bank"] == "Bank_A"
        and row["error_code"] == "E42"
    ):
        probabilities["RETRY_PAYMENT"] -= 0.20
        probabilities["ALTERNATE_PAYMENT"] += 0.15

    for intervention in probabilities:
        probabilities[intervention] = np.clip(
            probabilities[intervention],
            0.05,
            0.90,
        )

    return probabilities


def simulate_recovery(df, seed=42):
    """
    Create hidden ground-truth recovery outcomes.

    A separate seed allows independent, reproducible
    training and test simulations.
    """

    df = df.copy()

    rng = np.random.default_rng(seed)

    hidden_probabilities = []

    for _, row in df.iterrows():
        probabilities = get_hidden_probabilities(row)
        hidden_probabilities.append(probabilities)

    for intervention in INTERVENTIONS:

        name = intervention.lower()

        df[f"hidden_prob_{name}"] = [
            probabilities[intervention]
            for probabilities in hidden_probabilities
        ]

        random_values = rng.random(len(df))

        df[f"recovered_{name}"] = (
            random_values
            < df[f"hidden_prob_{name}"]
        )

        df[f"amount_recovered_{name}"] = np.where(
            df[f"recovered_{name}"],
            df["amount"],
            0,
        )

    return df


if __name__ == "__main__":

    df = pd.read_csv(
        "data/revenue_events.csv"
    )

    df = simulate_recovery(
        df,
        seed=42,
    )

    print(
        "Total events:",
        len(df),
    )

    print()

    for intervention in INTERVENTIONS:

        name = intervention.lower()

        recovered_count = df[
            f"recovered_{name}"
        ].sum()

        recovered_amount = df[
            f"amount_recovered_{name}"
        ].sum()

        print(intervention)

        print(
            "  Recovered events:",
            recovered_count,
        )

        print(
            f"  Amount recovered: "
            f"₹{recovered_amount:,.2f}"
        )

        print()

    output_path = (
        "data/recovery_outcomes.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved outcomes to: {output_path}"
    )