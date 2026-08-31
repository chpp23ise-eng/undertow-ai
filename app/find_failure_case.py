import pandas as pd

from decision_engine import load_model, make_decision
from recovery_service import load_outcomes


def main():

    model = load_model()

    events = pd.read_csv(
        "data/revenue_events.csv"
    )

    outcomes = load_outcomes()

    print("Searching for a failure case...")
    print()

    for _, event in events.iterrows():

        event_dict = event.to_dict()

        decision = make_decision(
            model,
            event_dict,
        )

        action = decision[
            "recommended_action"
        ]

        matching = outcomes[
            outcomes["event_id"]
            == event_dict["event_id"]
        ]

        if matching.empty:
            continue

        row = matching.iloc[0]

        column = (
            "amount_recovered_"
            + action.lower()
        )

        actual_recovery = row[column]

        if actual_recovery == 0:

            print(
                "FOUND FAILURE CASE"
            )
            print(
                "==================="
            )
            print()

            print(
                f"Event: "
                f"{event_dict['event_id']}"
            )

            print(
                f"Amount: "
                f"₹{event_dict['amount']:,.2f}"
            )

            print(
                f"Event type: "
                f"{event_dict['event_type']}"
            )

            print(
                f"Bank: "
                f"{event_dict['bank']}"
            )

            print(
                f"Error: "
                f"{event_dict['error_code']}"
            )

            print()

            print(
                f"Best action: {action}"
            )

            print(
                f"Predicted probability: "
                f"{decision['recovery_probability']:.2%}"
            )

            print(
                f"Expected recovery: "
                f"₹{decision['expected_recovery']:,.2f}"
            )

            print()

            print(
                "Actual result: "
                "NOT_RECOVERED"
            )

            print(
                "Actual recovered: ₹0.00"
            )

            print()

            print(
                "Use this event to demonstrate "
                "multi-attempt recovery."
            )

            return

    print(
        "No failure case found."
    )


if __name__ == "__main__":
    main()