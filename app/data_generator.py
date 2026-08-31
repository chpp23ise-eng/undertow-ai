import numpy as np
import pandas as pd


# Make the generated data reproducible
np.random.seed(42)

NUM_EVENTS = 5000

BANKS = ["Bank_A", "Bank_B", "Bank_C", "Bank_D"]
PAYMENT_METHODS = ["UPI", "CARD", "NETBANKING", "WALLET"]
EVENT_TYPES = [
    "PAYMENT_FAILED",
    "CHECKOUT_ABANDONED",
    "SUBSCRIPTION_FAILED",
    "INVOICE_OVERDUE",
]

ERROR_CODES = ["E11", "E17", "E23", "E42"]
PRODUCTS = [f"P{i:03d}" for i in range(1, 21)]


def generate_data(num_events=NUM_EVENTS):
    """Generate synthetic merchant revenue-loss events."""

    data = []

    for i in range(num_events):
        bank = np.random.choice(BANKS)
        error = np.random.choice(ERROR_CODES)
        event_type = np.random.choice(EVENT_TYPES)

        amount = round(np.random.uniform(500, 25000), 2)

        customer_id = f"C{np.random.randint(1, 1001):04d}"
        product_id = np.random.choice(PRODUCTS)
        payment_method = np.random.choice(PAYMENT_METHODS)

        # Create a hidden systemic pattern.
        # Undertow should eventually discover this pattern.
        if np.random.random() < 0.20:
            bank = "Bank_A"
            error = "E42"

        data.append(
            {
                "event_id": f"E{i + 1:05d}",
                "customer_id": customer_id,
                "amount": amount,
                "event_type": event_type,
                "bank": bank,
                "error_code": error,
                "product_id": product_id,
                "payment_method": payment_method,
            }
        )

    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate_data()

    output_path = "data/revenue_events.csv"
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} events.")
    print(f"Saved to: {output_path}")
    print()
    print(df.head())