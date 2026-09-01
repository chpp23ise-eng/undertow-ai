import numpy as np
import pandas as pd


DECISIONS_PATH = "data/experiment_decisions.csv"
OUTCOMES_PATH = "data/experiment_test_outcomes.csv"
PORTFOLIO_PATH = "data/portfolio_selected.csv"

CAPACITY = 1000

np.random.seed(42)


def load_data():
    """Load Undertow decisions, outcomes, and selected portfolio."""

    decisions = pd.read_csv(
        DECISIONS_PATH
    )

    outcomes = pd.read_csv(
        OUTCOMES_PATH
    )

    portfolio = pd.read_csv(
        PORTFOLIO_PATH
    )

    return decisions, outcomes, portfolio


def get_actual_recovery(row):
    """Return the actual recovery for the intervention chosen."""

    action = row["intervention"]

    if action == "RETRY_PAYMENT":
        return row[
            "amount_recovered_retry_payment"
        ]

    if action == "SEND_REMINDER":
        return row[
            "amount_recovered_send_reminder"
        ]

    if action == "ALTERNATE_PAYMENT":
        return row[
            "amount_recovered_alternate_payment"
        ]

    return 0.0


def attach_actual_outcomes(
    decisions,
    outcomes,
):
    """Attach actual recovery to every decision."""

    outcome_columns = [
        "event_id",
        "amount_recovered_retry_payment",
        "amount_recovered_send_reminder",
        "amount_recovered_alternate_payment",
    ]

    merged = decisions.merge(
        outcomes[outcome_columns],
        on="event_id",
        how="inner",
    )

    merged["actual_recovery"] = (
        merged.apply(
            get_actual_recovery,
            axis=1,
        )
    )

    return merged


def evaluate_random_strategy(
    decisions,
    capacity,
):
    """Select a random set of opportunities."""

    sample = decisions.sample(
        n=capacity,
        random_state=42,
    )

    return sample


def evaluate_highest_value_strategy(
    decisions,
    capacity,
):
    """
    Select the opportunities with the
    highest transaction amounts.
    """

    return (
        decisions
        .sort_values(
            "amount",
            ascending=False,
        )
        .head(capacity)
    )


def evaluate_undertow_strategy(
    decisions,
    portfolio,
):
    """Use Undertow's expected-recovery portfolio."""

    portfolio_ids = set(
        portfolio["event_id"]
    )

    return decisions[
        decisions["event_id"].isin(
            portfolio_ids
        )
    ].copy()


def calculate_actual_recovery(
    selected,
    outcomes,
):
    """Calculate actual money recovered by a strategy."""

    outcome_columns = [
        "event_id",
        "amount_recovered_retry_payment",
        "amount_recovered_send_reminder",
        "amount_recovered_alternate_payment",
    ]

    merged = selected.merge(
        outcomes[outcome_columns],
        on="event_id",
        how="inner",
    )

    merged["actual_recovery"] = (
        merged.apply(
            get_actual_recovery,
            axis=1,
        )
    )

    return merged[
        "actual_recovery"
    ].sum()


def main():

    print(
        "Loading portfolio data..."
    )

    decisions, outcomes, portfolio = (
        load_data()
    )

    print(
        f"Total opportunities: "
        f"{len(decisions):,}"
    )

    print(
        f"Recovery capacity: "
        f"{CAPACITY:,}"
    )

    # -----------------------------------------------------
    # Prepare decisions with actual outcomes.
    # -----------------------------------------------------

    decisions_with_outcomes = (
        attach_actual_outcomes(
            decisions,
            outcomes,
        )
    )

    # -----------------------------------------------------
    # Strategy 1: Random
    # -----------------------------------------------------

    random_selection = (
        evaluate_random_strategy(
            decisions_with_outcomes,
            CAPACITY,
        )
    )

    random_recovery = (
        random_selection[
            "actual_recovery"
        ].sum()
    )

    # -----------------------------------------------------
    # Strategy 2: Highest transaction value
    # -----------------------------------------------------

    highest_value_selection = (
        evaluate_highest_value_strategy(
            decisions_with_outcomes,
            CAPACITY,
        )
    )

    highest_value_recovery = (
        highest_value_selection[
            "actual_recovery"
        ].sum()
    )

    # -----------------------------------------------------
    # Strategy 3: Undertow
    # -----------------------------------------------------

    undertow_selection = (
        evaluate_undertow_strategy(
            decisions_with_outcomes,
            portfolio,
        )
    )

    undertow_recovery = (
        undertow_selection[
            "actual_recovery"
        ].sum()
    )

    # -----------------------------------------------------
    # Print results.
    # -----------------------------------------------------

    print()
    print(
        "PORTFOLIO STRATEGY EVALUATION"
    )
    print(
        "=============================="
    )
    print()

    print(
        f"Random {CAPACITY:,}: "
        f"₹{random_recovery:,.2f}"
    )

    print(
        f"Highest Value {CAPACITY:,}: "
        f"₹{highest_value_recovery:,.2f}"
    )

    print(
        f"Undertow {CAPACITY:,}: "
        f"₹{undertow_recovery:,.2f}"
    )

    print()

    # -----------------------------------------------------
    # Calculate uplift.
    # -----------------------------------------------------

    if random_recovery > 0:

        random_uplift = (
            (
                undertow_recovery
                - random_recovery
            )
            / random_recovery
            * 100
        )

    else:

        random_uplift = 0.0

    if highest_value_recovery > 0:

        highest_value_uplift = (
            (
                undertow_recovery
                - highest_value_recovery
            )
            / highest_value_recovery
            * 100
        )

    else:

        highest_value_uplift = 0.0

    print(
        f"Undertow uplift vs Random: "
        f"{random_uplift:.2f}%"
    )

    print(
        f"Undertow uplift vs Highest Value: "
        f"{highest_value_uplift:.2f}%"
    )

    # -----------------------------------------------------
    # Compare predicted vs actual.
    # -----------------------------------------------------

    undertow_predicted = (
        undertow_selection[
            "expected_recovery"
        ].sum()
    )

    print()
    print(
        "UNDERTOW PREDICTION VS ACTUAL"
    )
    print(
        "-----------------------------"
    )

    print(
        f"Predicted recovery: "
        f"₹{undertow_predicted:,.2f}"
    )

    print(
        f"Actual recovery: "
        f"₹{undertow_recovery:,.2f}"
    )

    if undertow_predicted > 0:

        prediction_error = (
            (
                undertow_recovery
                - undertow_predicted
            )
            / undertow_predicted
            * 100
        )

    else:

        prediction_error = 0.0

    print(
        f"Prediction error: "
        f"{prediction_error:.2f}%"
    )

    # -----------------------------------------------------
    # Save evaluation results.
    # -----------------------------------------------------

    results = pd.DataFrame(
        [
            {
                "strategy": "RANDOM",
                "capacity": CAPACITY,
                "actual_recovery":
                    random_recovery,
            },
            {
                "strategy": "HIGHEST_VALUE",
                "capacity": CAPACITY,
                "actual_recovery":
                    highest_value_recovery,
            },
            {
                "strategy": "UNDERTOW",
                "capacity": CAPACITY,
                "actual_recovery":
                    undertow_recovery,
            },
        ]
    )

    output_path = (
        "data/portfolio_evaluation.csv"
    )

    results.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        f"Saved evaluation to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()