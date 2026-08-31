import pandas as pd


OUTCOMES_PATH = "data/experiment_test_outcomes.csv"
DECISIONS_PATH = "data/experiment_decisions.csv"


def main():

    print("Loading test outcomes...")
    outcomes = pd.read_csv(OUTCOMES_PATH)

    print("Loading Undertow decisions...")
    decisions = pd.read_csv(DECISIONS_PATH)

    print()
    print("UNDERTOW LEARNING REPORT")
    print("========================")
    print()

    # -----------------------------------------------------
    # 1. Prediction vs actual outcome
    # -----------------------------------------------------

    print("OVERALL PERFORMANCE")
    print("-------------------")

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

    actual_recovery = []

    for _, row in merged.iterrows():

        if row["intervention"] == "RETRY_PAYMENT":
            amount = row[
                "amount_recovered_retry_payment"
            ]

        elif row["intervention"] == "SEND_REMINDER":
            amount = row[
                "amount_recovered_send_reminder"
            ]

        else:
            amount = row[
                "amount_recovered_alternate_payment"
            ]

        actual_recovery.append(amount)

    merged["actual_recovery"] = actual_recovery

    merged["actual_recovered"] = (
        merged["actual_recovery"] > 0
    )

    print(
        f"Events evaluated: {len(merged)}"
    )

    print(
        f"Predicted recovery: "
        f"₹{merged['expected_recovery'].sum():,.2f}"
    )

    print(
        f"Actual recovery: "
        f"₹{merged['actual_recovery'].sum():,.2f}"
    )

    print(
        f"Actual recovery rate: "
        f"{merged['actual_recovered'].mean():.2%}"
    )

    print()

    # -----------------------------------------------------
    # 2. Performance by intervention
    # -----------------------------------------------------

    print("PERFORMANCE BY INTERVENTION")
    print("---------------------------")

    intervention_report = (
        merged
        .groupby("intervention")
        .agg(
            events=("event_id", "count"),
            predicted_recovery=(
                "expected_recovery",
                "sum",
            ),
            actual_recovery=(
                "actual_recovery",
                "sum",
            ),
            recovery_rate=(
                "actual_recovered",
                "mean",
            ),
        )
        .sort_values(
            "actual_recovery",
            ascending=False,
        )
    )

    print(
        intervention_report.to_string()
    )

    print()

    # -----------------------------------------------------
    # 3. Performance by event type
    # -----------------------------------------------------

    print("PERFORMANCE BY EVENT TYPE")
    print("-------------------------")

    event_report = (
        merged
        .groupby("event_type")
        .agg(
            events=("event_id", "count"),
            predicted_recovery=(
                "expected_recovery",
                "sum",
            ),
            actual_recovery=(
                "actual_recovery",
                "sum",
            ),
            recovery_rate=(
                "actual_recovered",
                "mean",
            ),
        )
        .sort_values(
            "actual_recovery",
            ascending=False,
        )
    )

    print(
        event_report.to_string()
    )

    print()

    # -----------------------------------------------------
    # 4. Performance by bank
    # -----------------------------------------------------

    print("PERFORMANCE BY BANK")
    print("--------------------")

    bank_report = (
        merged
        .groupby("bank")
        .agg(
            events=("event_id", "count"),
            predicted_recovery=(
                "expected_recovery",
                "sum",
            ),
            actual_recovery=(
                "actual_recovery",
                "sum",
            ),
            recovery_rate=(
                "actual_recovered",
                "mean",
            ),
        )
        .sort_values(
            "actual_recovery",
            ascending=False,
        )
    )

    print(
        bank_report.to_string()
    )

    print()

    # -----------------------------------------------------
    # 5. Performance by error code
    # -----------------------------------------------------

    print("PERFORMANCE BY ERROR CODE")
    print("-------------------------")

    error_report = (
        merged
        .groupby("error_code")
        .agg(
            events=("event_id", "count"),
            predicted_recovery=(
                "expected_recovery",
                "sum",
            ),
            actual_recovery=(
                "actual_recovery",
                "sum",
            ),
            recovery_rate=(
                "actual_recovered",
                "mean",
            ),
        )
        .sort_values(
            "actual_recovery",
            ascending=False,
        )
    )

    print(
        error_report.to_string()
    )

    print()

    # -----------------------------------------------------
    # 6. Prediction calibration
    # -----------------------------------------------------

    merged["probability_bucket"] = pd.cut(
        merged["recovery_probability"],
        bins=[
            0.0,
            0.2,
            0.4,
            0.6,
            0.8,
            1.0,
        ],
        labels=[
            "0-20%",
            "20-40%",
            "40-60%",
            "60-80%",
            "80-100%",
        ],
        include_lowest=True,
    )

    calibration = (
        merged
        .groupby(
            "probability_bucket",
            observed=True,
        )
        .agg(
            events=("event_id", "count"),
            predicted_probability=(
                "recovery_probability",
                "mean",
            ),
            actual_recovery_rate=(
                "actual_recovered",
                "mean",
            ),
        )
    )

    print("PREDICTION CALIBRATION")
    print("----------------------")

    print(
        calibration.to_string()
    )

    print()

    print(
        "Learning report complete."
    )


if __name__ == "__main__":
    main()