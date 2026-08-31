import numpy as np
import pandas as pd


DECISIONS_PATH = "data/experiment_decisions.csv"
OUTCOMES_PATH = "data/experiment_test_outcomes.csv"


INTERVENTION_AMOUNT_COLUMNS = {
    "RETRY_PAYMENT": "amount_recovered_retry_payment",
    "SEND_REMINDER": "amount_recovered_send_reminder",
    "ALTERNATE_PAYMENT": "amount_recovered_alternate_payment",
}


def calculate_strategy_recovery(
    outcomes,
    intervention,
):
    """Calculate actual recovery for a fixed strategy."""

    column = INTERVENTION_AMOUNT_COLUMNS[
        intervention
    ]

    return outcomes[column].sum()


def calculate_undertow_recovery(
    decisions,
    outcomes,
):
    """Calculate actual recovery from Undertow's selected actions."""

    merged = decisions.merge(
        outcomes[
            [
                "event_id",
                "amount_recovered_retry_payment",
                "amount_recovered_send_reminder",
                "amount_recovered_alternate_payment",
            ]
        ],
        on="event_id",
        how="inner",
    )

    recovered_amounts = []

    for _, row in merged.iterrows():

        column = INTERVENTION_AMOUNT_COLUMNS[
            row["intervention"]
        ]

        recovered_amounts.append(
            row[column]
        )

    return sum(recovered_amounts)


def calculate_random_recovery(
    outcomes,
    seed=42,
):
    """Calculate recovery from a random intervention strategy."""

    rng = np.random.default_rng(seed)

    interventions = [
        "RETRY_PAYMENT",
        "SEND_REMINDER",
        "ALTERNATE_PAYMENT",
    ]

    random_choices = rng.choice(
        interventions,
        size=len(outcomes),
    )

    recovered = []

    for index, intervention in enumerate(
        random_choices
    ):

        column = INTERVENTION_AMOUNT_COLUMNS[
            intervention
        ]

        recovered.append(
            outcomes.iloc[index][column]
        )

    return sum(recovered)


def calculate_uplift(
    strategy_recovery,
    baseline_recovery,
):
    """Calculate percentage uplift."""

    if baseline_recovery == 0:
        return 0.0

    return (
        (
            strategy_recovery
            - baseline_recovery
        )
        / baseline_recovery
    ) * 100


def main():

    print("Loading experiment decisions...")
    decisions = pd.read_csv(
        DECISIONS_PATH
    )

    print("Loading held-out outcomes...")
    outcomes = pd.read_csv(
        OUTCOMES_PATH
    )

    print()
    print("FINAL UNDERTOW EXPERIMENT")
    print("=========================")
    print()

    print(
        f"Test events: {len(outcomes)}"
    )

    print()

    # Baseline 1: always retry.
    retry_recovery = calculate_strategy_recovery(
        outcomes,
        "RETRY_PAYMENT",
    )

    # Baseline 2: always reminder.
    reminder_recovery = calculate_strategy_recovery(
        outcomes,
        "SEND_REMINDER",
    )

    # Baseline 3: random strategy.
    random_recovery = calculate_random_recovery(
        outcomes,
        seed=42,
    )

    # Undertow.
    undertow_recovery = calculate_undertow_recovery(
        decisions,
        outcomes,
    )

    print("ACTUAL RECOVERY")
    print("----------------")

    print(
        f"Always Retry: "
        f"₹{retry_recovery:,.2f}"
    )

    print(
        f"Always Reminder: "
        f"₹{reminder_recovery:,.2f}"
    )

    print(
        f"Random Strategy: "
        f"₹{random_recovery:,.2f}"
    )

    print(
        f"Undertow: "
        f"₹{undertow_recovery:,.2f}"
    )

    print()

    print("UPLIFT")
    print("------")

    retry_uplift = calculate_uplift(
        undertow_recovery,
        retry_recovery,
    )

    reminder_uplift = calculate_uplift(
        undertow_recovery,
        reminder_recovery,
    )

    random_uplift = calculate_uplift(
        undertow_recovery,
        random_recovery,
    )

    print(
        f"vs Always Retry: "
        f"{retry_uplift:.2f}%"
    )

    print(
        f"vs Always Reminder: "
        f"{reminder_uplift:.2f}%"
    )

    print(
        f"vs Random: "
        f"{random_uplift:.2f}%"
    )

    print()

    print("Undertow action distribution:")
    print(
        decisions["intervention"]
        .value_counts()
    )


if __name__ == "__main__":
    main()