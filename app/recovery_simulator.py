import numpy as np
import pandas as pd


np.random.seed(42)


def assign_recovery_probability(row):
    """
    Hidden ground-truth probability.

    Undertow will NOT see this value directly.
    The simulator uses it to determine whether
    a recovery attempt succeeds.
    """

    probability = 0.40

    # Different recovery behavior for different event types
    if row["event_type"] == "PAYMENT_FAILED":
        probability += 0.15

    elif row["event_type"] == "CHECKOUT_ABANDONED":
        probability += 0.05

    elif row["event_type"] == "SUBSCRIPTION_FAILED":
        probability += 0.10

    elif row["event_type"] == "INVOICE_OVERDUE":
        probability -= 0.10

    # Some payment failures are harder to recover
    if row["error_code"] == "E42":
        probability -= 0.10

    # Bank A has a hidden degradation pattern
    if row["bank"] == "Bank_A" and row["error_code"] == "E42":
        probability -= 0.15

    # Keep probability in a sensible range
    return np.clip(probability, 0.05, 0.90)


def simulate_recovery(df):
    """Simulate what happens when recovery is attempted."""

    df = df.copy()

    # Hidden value used only by the simulator
    df["hidden_recovery_probability"] = df.apply(
        assign_recovery_probability,
        axis=1,
    )

    # Simulate the actual outcome
    random_values = np.random.random(len(df))

    df["recovered"] = (
        random_values < df["hidden_recovery_probability"]
    )

    df["amount_recovered"] = np.where(
        df["recovered"],
        df["amount"],
        0,
    )

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/revenue_events.csv")

    df = simulate_recovery(df)

    print("Total events:", len(df))
    print()

    print("Recovery outcomes:")
    print(df["recovered"].value_counts())
    print()

    print("Total amount:")
    print(f"₹{df['amount'].sum():,.2f}")
    print()

    print("Total amount recovered:")
    print(f"₹{df['amount_recovered'].sum():,.2f}")