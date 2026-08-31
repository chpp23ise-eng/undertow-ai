import pandas as pd

from decision_engine import load_model, make_decision
from governor import evaluate_action
from executor import execute_action
from recovery_service import load_outcomes, execute_recovery
from audit import write_audit_log


CONTACT_HISTORY = {}


def run_workflow(model, outcomes, event):
    """
    Run one complete Undertow recovery workflow.

    Flow:
        Event
        -> Decision
        -> Governor
        -> Executor
        -> Recovery outcome
        -> Audit log
    """

    event_id = event["event_id"]

    contact_count = CONTACT_HISTORY.get(
        event_id,
        0,
    )

    # 1. Decide the best intervention.
    decision = make_decision(
        model,
        event,
    )

    action = decision["recommended_action"]
    expected_recovery = decision["expected_recovery"]

    # 2. Check stopping rules.
    governor_result = evaluate_action(
        contact_count=contact_count,
        expected_recovery=expected_recovery,
        action=action,
    )

    # Default result for a blocked action.
    if governor_result["decision"] != "ALLOW":

        if governor_result["decision"] == "ESCALATE":
            final_status = "HUMAN_REVIEW_REQUIRED"
        else:
            final_status = "RECOVERY_STOPPED"

        result = {
            "event_id": event_id,
            "amount": event["amount"],
            "recommended_action": action,
            "recovery_probability": decision[
                "recovery_probability"
            ],
            "expected_recovery": expected_recovery,
            "contact_count": contact_count,
            "governor_decision": governor_result[
                "decision"
            ],
            "governor_reason": governor_result[
                "reason"
            ],
            "execution_status": "NOT_EXECUTED",
            "actual_status": "NOT_EXECUTED",
            "amount_recovered": 0.0,
            "final_status": final_status,
        }

        # Record even blocked decisions.
        write_audit_log(result)

        return result

    # 3. Execute the approved action.
    execution_result = execute_action(
        event,
        action,
    )

    CONTACT_HISTORY[event_id] = (
        contact_count + 1
    )

    # 4. Get the actual simulated outcome.
    recovery_result = execute_recovery(
        outcomes=outcomes,
        event_id=event_id,
        action=action,
    )

    result = {
        "event_id": event_id,
        "amount": event["amount"],
        "recommended_action": action,
        "recovery_probability": decision[
            "recovery_probability"
        ],
        "expected_recovery": expected_recovery,
        "contact_count": contact_count,
        "governor_decision": governor_result[
            "decision"
        ],
        "governor_reason": governor_result[
            "reason"
        ],
        "execution_status": execution_result[
            "status"
        ],
        "actual_status": recovery_result[
            "status"
        ],
        "amount_recovered": recovery_result[
            "amount_recovered"
        ],
        "final_status": recovery_result[
            "status"
        ],
    }

    # 5. Record the complete decision trail.
    write_audit_log(result)

    return result


def print_workflow_result(result):
    """Display the workflow result."""

    print()
    print("UNDERTOW RECOVERY WORKFLOW")
    print("==========================")
    print()

    print(f"Event: {result['event_id']}")
    print(f"Amount: ₹{result['amount']:,.2f}")
    print(
        f"Previous contacts: "
        f"{result['contact_count']}"
    )

    print()

    print(
        f"Recommended action: "
        f"{result['recommended_action']}"
    )

    print(
        f"Recovery probability: "
        f"{result['recovery_probability']:.2%}"
    )

    print(
        f"Expected recovery: "
        f"₹{result['expected_recovery']:,.2f}"
    )

    print()

    print(
        f"Governor: "
        f"{result['governor_decision']}"
    )

    print(
        f"Reason: "
        f"{result['governor_reason']}"
    )

    print()

    print(
        f"Execution: "
        f"{result['execution_status']}"
    )

    print(
        f"Actual outcome: "
        f"{result['actual_status']}"
    )

    print(
        f"Actual amount recovered: "
        f"₹{result['amount_recovered']:,.2f}"
    )

    print()

    print(
        f"Final status: "
        f"{result['final_status']}"
    )

    print()
    print("Audit log updated:")
    print("data/audit_log.jsonl")


if __name__ == "__main__":

    model = load_model()
    outcomes = load_outcomes()

    events = pd.read_csv(
        "data/revenue_events.csv"
    )

    event = events.iloc[0].to_dict()

    result = run_workflow(
        model=model,
        outcomes=outcomes,
        event=event,
    )

    print_workflow_result(result)