import numpy as np
import pandas as pd


OUTCOMES_PATH = "data/recovery_outcomes.csv"
DECISIONS_PATH = "data/decisions.csv"


def evaluate_fixed_retry(outcomes):
    """Always use RETRY_PAYMENT."""

    return outcomes["amount_recovered_retry_payment"].sum()


def evaluate_random(outcomes):
    """
    Randomly choose one intervention for each event.
    """

    np.random.seed(42)

    interventions = [
        "retry_payment",
        "send_reminder",
        "alternate_payment",
    ]

    choices = np.random.choice(
        interventions,
        size=len(outcomes),
    )

    recovered_amount = 0

    for i, intervention in enumerate(choices):
        recovered_amount += outcomes.iloc[i][
            f"amount_recovered_{intervention}"
        ]

    return recovered_amount


def evaluate_undertow(outcomes, decisions):
    """
    Apply Undertow's selected intervention to the
    actual simulated outcome.
    """

    merged = decisions.merge(
        outcomes,
        on="event_id",
        how="inner",
    )

    recovered_amount = 0

    for _, row in merged.iterrows():

        intervention = row["intervention"].lower()

        recovered_amount += row[
            f"amount_recovered_{intervention}"
        ]

    return recovered_amount


def calculate_uplift(undertow, baseline):
    """Calculate percentage uplift over a baseline."""

    if baseline == 0:
        return 0

    return ((undertow - baseline) / baseline) * 100


def main():

    print("Loading outcomes...")
    outcomes = pd.read_csv(OUTCOMES_PATH)

    print("Loading Undertow decisions...")
    decisions = pd.read_csv(DECISIONS_PATH)

    print()

    # Evaluate strategies
    fixed_retry = evaluate_fixed_retry(
        outcomes
    )

    random_strategy = evaluate_random(
        outcomes
    )

    undertow = evaluate_undertow(
        outcomes,
        decisions,
    )

    # Calculate uplift
    undertow_vs_retry = calculate_uplift(
        undertow,
        fixed_retry,
    )

    undertow_vs_random = calculate_uplift(
        undertow,
        random_strategy,
    )

    print("RECOVERY STRATEGY EVALUATION")
    print("============================")
    print()

    print(
        f"Fixed Retry: "
        f"₹{fixed_retry:,.2f}"
    )

    print(
        f"Random Strategy: "
        f"₹{random_strategy:,.2f}"
    )

    print(
        f"Undertow: "
        f"₹{undertow:,.2f}"
    )

    print()

    print(
        f"Undertow uplift vs Fixed Retry: "
        f"{undertow_vs_retry:.2f}%"
    )

    print(
        f"Undertow uplift vs Random: "
        f"{undertow_vs_random:.2f}%"
    )


if __name__ == "__main__":
    main()