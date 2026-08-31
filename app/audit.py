import json
import os
from datetime import datetime


AUDIT_PATH = "data/audit_log.jsonl"


def write_audit_log(result):
    """
    Append one workflow result to the audit log.

    JSONL means every line is one independent JSON record.
    """

    os.makedirs("data", exist_ok=True)

    audit_record = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "event_id": result["event_id"],
        "amount": result["amount"],
        "recommended_action": result[
            "recommended_action"
        ],
        "recovery_probability": result[
            "recovery_probability"
        ],
        "expected_recovery": result[
            "expected_recovery"
        ],
        "contact_count": result[
            "contact_count"
        ],
        "governor_decision": result[
            "governor_decision"
        ],
        "governor_reason": result[
            "governor_reason"
        ],
        "execution_status": result[
            "execution_status"
        ],
        "actual_status": result[
            "actual_status"
        ],
        "amount_recovered": result[
            "amount_recovered"
        ],
        "final_status": result[
            "final_status"
        ],
    }

    with open(
        AUDIT_PATH,
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                audit_record,
                default=lambda value: (
                    value.item()
                    if hasattr(value, "item")
                    else str(value)
                ),
            )
            + "\n"
        )

    return audit_record


if __name__ == "__main__":

    example_result = {
        "event_id": "E00001",
        "amount": 4994.15,
        "recommended_action": "ALTERNATE_PAYMENT",
        "recovery_probability": 0.7613,
        "expected_recovery": 3802.11,
        "contact_count": 0,
        "governor_decision": "ALLOW",
        "governor_reason": (
            "Action satisfies current recovery rules."
        ),
        "execution_status": "EXECUTED",
        "actual_status": "RECOVERED",
        "amount_recovered": 4994.15,
        "final_status": "RECOVERED",
    }

    record = write_audit_log(
        example_result
    )

    print("Audit record created.")
    print(json.dumps(record, indent=2))
    print()
    print(f"Saved to: {AUDIT_PATH}")