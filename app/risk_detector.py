import pandas as pd


RISK_PROBABILITY = {
    "PAYMENT_FAILED": 0.80,
    "CHECKOUT_ABANDONED": 0.65,
    "SUBSCRIPTION_FAILED": 0.75,
    "INVOICE_OVERDUE": 0.60,
}


def calculate_revenue_at_risk(df):
    """Calculate estimated revenue at risk for each event."""

    df = df.copy()

    df["risk_probability"] = df["event_type"].map(RISK_PROBABILITY)

    df["revenue_at_risk"] = (
        df["amount"] * df["risk_probability"]
    )

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/revenue_events.csv")

    df = calculate_revenue_at_risk(df)

    print("Total revenue involved:")
    print(f"₹{df['amount'].sum():,.2f}")
    print()

    print("Estimated revenue at risk:")
    print(f"₹{df['revenue_at_risk'].sum():,.2f}")
    print()

    print("Top 10 events by revenue at risk:")
    print(
        df[
            [
                "event_id",
                "customer_id",
                "amount",
                "event_type",
                "risk_probability",
                "revenue_at_risk",
            ]
        ]
        .sort_values("revenue_at_risk", ascending=False)
        .head(10)
        .to_string(index=False)
    )