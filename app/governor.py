MAX_CONTACTS = 3

MIN_EXPECTED_RECOVERY = 500


def evaluate_action(
    contact_count,
    expected_recovery,
    action,
):
    """
    Decide whether an automated recovery action
    is allowed.

    The governor is deterministic and does not
    depend on an LLM.
    """

    # Rule 1: Never contact a customer beyond
    # the maximum automated contact limit.
    if contact_count >= MAX_CONTACTS:
        return {
            "decision": "ESCALATE",
            "reason": "Maximum contact limit reached.",
        }

    # Rule 2: Do not spend effort on opportunities
    # with very little expected recovery.
    if expected_recovery < MIN_EXPECTED_RECOVERY:
        return {
            "decision": "STOP",
            "reason": "Expected recovery is below minimum threshold.",
        }

    # Rule 3: Otherwise the action is allowed.
    return {
        "decision": "ALLOW",
        "action": action,
        "reason": "Action satisfies current recovery rules.",
    }


if __name__ == "__main__":

    print("UNDERTOW STOPPING-RULE GOVERNOR")
    print("===============================")
    print()

    examples = [
        {
            "contact_count": 0,
            "expected_recovery": 5000,
            "action": "SEND_REMINDER",
        },
        {
            "contact_count": 2,
            "expected_recovery": 5000,
            "action": "ALTERNATE_PAYMENT",
        },
        {
            "contact_count": 3,
            "expected_recovery": 5000,
            "action": "SEND_REMINDER",
        },
        {
            "contact_count": 1,
            "expected_recovery": 200,
            "action": "RETRY_PAYMENT",
        },
    ]

    for example in examples:

        result = evaluate_action(
            contact_count=example["contact_count"],
            expected_recovery=example["expected_recovery"],
            action=example["action"],
        )

        print(
            f"Contacts: {example['contact_count']} | "
            f"Expected: ₹{example['expected_recovery']:,.0f} | "
            f"Action: {example['action']}"
        )

        print(
            f"Decision: {result['decision']}"
        )

        print(
            f"Reason: {result['reason']}"
        )

        print()