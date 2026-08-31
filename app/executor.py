from datetime import datetime


def execute_action(event, action):
    """
    Simulate executing a recovery action.

    This is a mock executor for our prototype.
    No real customer or payment system is contacted.
    """

    timestamp = datetime.now().isoformat(timespec="seconds")

    if action == "RETRY_PAYMENT":
        message = "Payment retry initiated."

    elif action == "SEND_REMINDER":
        message = "Recovery reminder sent."

    elif action == "ALTERNATE_PAYMENT":
        message = "Alternate payment option offered."

    else:
        return {
            "event_id": event["event_id"],
            "action": action,
            "status": "FAILED",
            "message": "Unknown recovery action.",
            "timestamp": timestamp,
            "amount_recovered": 0,
        }

    return {
        "event_id": event["event_id"],
        "action": action,
        "status": "EXECUTED",
        "message": message,
        "timestamp": timestamp,
        "amount_recovered": 0,
    }


if __name__ == "__main__":

    example_event = {
        "event_id": "E00001",
        "amount": 4994.15,
    }

    actions = [
        "RETRY_PAYMENT",
        "SEND_REMINDER",
        "ALTERNATE_PAYMENT",
    ]

    print("UNDERTOW MOCK EXECUTOR")
    print("======================")
    print()

    for action in actions:

        result = execute_action(
            example_event,
            action,
        )

        print(f"Action: {result['action']}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Timestamp: {result['timestamp']}")
        print()