import pandas as pd


INPUT_PATH = "data/decisions.csv"
OUTPUT_PATH = "data/prioritized_opportunities.csv"


def prioritize_opportunities(df):
    """
    Rank recovery opportunities by expected revenue recovery.

    Higher expected recovery = higher priority.
    """

    df = df.copy()

    df["priority_score"] = df["expected_recovery"]

    df["priority"] = pd.cut(
        df["priority_score"],
        bins=[-1, 2500, 7500, float("inf")],
        labels=["LOW", "MEDIUM", "HIGH"],
    )

    return df.sort_values(
        "priority_score",
        ascending=False,
    ).reset_index(drop=True)


def main():

    print("Loading Undertow decisions...")

    df = pd.read_csv(INPUT_PATH)

    print(f"Opportunities: {len(df)}")
    print()

    prioritized = prioritize_opportunities(df)

    prioritized.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("Priority distribution:")
    print(
        prioritized["priority"]
        .value_counts()
    )

    print()
    print("Top 10 recovery opportunities:")
    print()

    print(
        prioritized[
            [
                "event_id",
                "amount",
                "event_type",
                "bank",
                "error_code",
                "intervention",
                "recovery_probability",
                "expected_recovery",
                "priority",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print()
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()