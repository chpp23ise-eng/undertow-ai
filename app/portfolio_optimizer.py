import pandas as pd


DECISIONS_PATH = "data/experiment_decisions.csv"


def optimize_portfolio(decisions, capacity):
    """
    Select the recovery opportunities that maximize
    expected recovered revenue under a limited action capacity.
    """

    if capacity <= 0:
        raise ValueError(
            "Capacity must be greater than zero."
        )

    if decisions.empty:
        return decisions.copy(), decisions.copy()

    decisions = decisions.copy()

    decisions = decisions.sort_values(
        "expected_recovery",
        ascending=False,
    ).reset_index(drop=True)

    selected = decisions.head(capacity).copy()

    deferred = decisions.iloc[
        capacity:
    ].copy()

    return selected, deferred


def calculate_portfolio_metrics(
    selected,
    deferred,
    all_decisions,
):
    """Calculate portfolio-level recovery metrics."""

    total_opportunity = (
        all_decisions[
            "expected_recovery"
        ].sum()
    )

    selected_recovery = (
        selected[
            "expected_recovery"
        ].sum()
    )

    deferred_recovery = (
        deferred[
            "expected_recovery"
        ].sum()
    )

    if total_opportunity > 0:
        captured_percentage = (
            selected_recovery
            / total_opportunity
        )
    else:
        captured_percentage = 0.0

    return {
        "total_events": len(
            all_decisions
        ),
        "selected_events": len(
            selected
        ),
        "deferred_events": len(
            deferred
        ),
        "total_expected_recovery": float(
            total_opportunity
        ),
        "selected_expected_recovery": float(
            selected_recovery
        ),
        "deferred_expected_recovery": float(
            deferred_recovery
        ),
        "captured_percentage": float(
            captured_percentage
        ),
    }


def print_report(
    metrics,
    capacity,
):
    """Print the portfolio optimization report."""

    print()
    print(
        "UNDERTOW PORTFOLIO OPTIMIZER"
    )
    print(
        "============================"
    )
    print()

    print(
        f"Total opportunities: "
        f"{metrics['total_events']:,}"
    )

    print(
        f"Recovery capacity: "
        f"{capacity:,}"
    )

    print(
        f"Selected opportunities: "
        f"{metrics['selected_events']:,}"
    )

    print(
        f"Deferred opportunities: "
        f"{metrics['deferred_events']:,}"
    )

    print()

    print(
        f"Total expected recovery: "
        f"₹{metrics['total_expected_recovery']:,.2f}"
    )

    print(
        f"Expected recovery from selected: "
        f"₹{metrics['selected_expected_recovery']:,.2f}"
    )

    print(
        f"Expected recovery deferred: "
        f"₹{metrics['deferred_expected_recovery']:,.2f}"
    )

    print(
        f"Recovery opportunity captured: "
        f"{metrics['captured_percentage']:.2%}"
    )


def main():

    print(
        "Loading Undertow decisions..."
    )

    decisions = pd.read_csv(
        DECISIONS_PATH
    )

    print(
        f"Opportunities loaded: "
        f"{len(decisions):,}"
    )

    print()

    # -----------------------------------------------------
    # Recovery capacity
    # -----------------------------------------------------

    capacity = 1000

    selected, deferred = (
        optimize_portfolio(
            decisions,
            capacity,
        )
    )

    metrics = (
        calculate_portfolio_metrics(
            selected,
            deferred,
            decisions,
        )
    )

    print_report(
        metrics,
        capacity,
    )

    # -----------------------------------------------------
    # Show selected opportunities
    # -----------------------------------------------------

    print()
    print(
        "TOP 10 SELECTED OPPORTUNITIES"
    )
    print(
        "-----------------------------"
    )

    display_columns = [
        "event_id",
        "amount",
        "event_type",
        "bank",
        "error_code",
        "intervention",
        "recovery_probability",
        "expected_recovery",
    ]

    print(
        selected[
            display_columns
        ]
        .head(10)
        .to_string(index=False)
    )

    # -----------------------------------------------------
    # Action distribution
    # -----------------------------------------------------

    print()
    print(
        "SELECTED ACTION DISTRIBUTION"
    )
    print(
        "----------------------------"
    )

    print(
        selected[
            "intervention"
        ].value_counts()
    )

    # -----------------------------------------------------
    # Save selected portfolio
    # -----------------------------------------------------

    output_path = (
        "data/portfolio_selected.csv"
    )

    selected.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        f"Saved selected portfolio to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()