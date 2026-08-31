import pandas as pd

from decision_engine import load_model, make_decision
from governor import evaluate_action
from executor import execute_action
from recovery_service import load_outcomes, execute_recovery
from audit import write_audit_log


MAX_ATTEMPTS = 3


def run_agent(model, outcomes, event):
    """
    Run Undertow as a bounded, stateful recovery agent.

    The agent:
        1. Gets the best available intervention from the model.
        2. Checks the action with the governor.
        3. Executes approved actions.
        4. Records the actual recovery outcome.
        5. Remembers previously attempted interventions.
        6. Stops after recovery, STOP, ESCALATE,
           or maximum attempts.
    """

    event_id = event["event_id"]
    contact_count = 0

    # Remember interventions already attempted.
    tried_actions = []

    # Store the complete attempt history.
    history = []

    print()
    print("UNDERTOW AGENT")
    print("==============")
    print()
    print(f"Event: {event_id}")
    print(f"Amount: ₹{event['amount']:,.2f}")
    print()

    while contact_count < MAX_ATTEMPTS:

        print(
            f"Attempt {contact_count + 1}"
        )

        # -------------------------------------------------
        # 1. ML chooses the best AVAILABLE intervention.
        # -------------------------------------------------

        decision = make_decision(
            model=model,
            event=event,
            excluded_interventions=tried_actions,
        )

        action = decision[
            "recommended_action"
        ]

        recovery_probability = float(
            decision["recovery_probability"]
        )

        expected_recovery = float(
            decision["expected_recovery"]
        )

        # -------------------------------------------------
        # 2. No interventions remain.
        # -------------------------------------------------

        if action is None:

            result = {
                "event_id": event_id,
                "amount": event["amount"],
                "recommended_action": None,
                "recovery_probability": 0.0,
                "expected_recovery": 0.0,
                "contact_count": contact_count,
                "governor_decision": "ESCALATE",
                "governor_reason": (
                    "All available interventions "
                    "have already been attempted."
                ),
                "execution_status": "NOT_EXECUTED",
                "actual_status": "ESCALATED",
                "amount_recovered": 0.0,
                "final_status": "HUMAN_REVIEW_REQUIRED",
                "history": history,
            }

            write_audit_log(result)

            print()
            print("Governor: ESCALATE")
            print(
                "Reason: All available "
                "interventions have already "
                "been attempted."
            )
            print()
            print(
                "Final status: "
                "HUMAN_REVIEW_REQUIRED"
            )

            return result

        print(
            f"Recommended action: {action}"
        )

        print(
            f"Recovery probability: "
            f"{recovery_probability:.2%}"
        )

        print(
            f"Expected recovery: "
            f"₹{expected_recovery:,.2f}"
        )

        # -------------------------------------------------
        # 3. Governor checks the action.
        # -------------------------------------------------

        governor_result = evaluate_action(
            contact_count=contact_count,
            expected_recovery=expected_recovery,
            action=action,
        )

        governor_decision = governor_result[
            "decision"
        ]

        governor_reason = governor_result[
            "reason"
        ]

        print(
            f"Governor: {governor_decision}"
        )

        print(
            f"Reason: {governor_reason}"
        )

        # -------------------------------------------------
        # 4. STOP.
        # -------------------------------------------------

        if governor_decision == "STOP":

            result = {
                "event_id": event_id,
                "amount": event["amount"],
                "recommended_action": action,
                "recovery_probability": recovery_probability,
                "expected_recovery": expected_recovery,
                "contact_count": contact_count,
                "governor_decision": "STOP",
                "governor_reason": governor_reason,
                "execution_status": "NOT_EXECUTED",
                "actual_status": "STOPPED",
                "amount_recovered": 0.0,
                "final_status": "RECOVERY_STOPPED",
                "history": history,
            }

            write_audit_log(result)

            print()
            print(
                "Final status: RECOVERY_STOPPED"
            )

            return result

        # -------------------------------------------------
        # 5. ESCALATE.
        # -------------------------------------------------

        if governor_decision == "ESCALATE":

            result = {
                "event_id": event_id,
                "amount": event["amount"],
                "recommended_action": action,
                "recovery_probability": recovery_probability,
                "expected_recovery": expected_recovery,
                "contact_count": contact_count,
                "governor_decision": "ESCALATE",
                "governor_reason": governor_reason,
                "execution_status": "NOT_EXECUTED",
                "actual_status": "ESCALATED",
                "amount_recovered": 0.0,
                "final_status": "HUMAN_REVIEW_REQUIRED",
                "history": history,
            }

            write_audit_log(result)

            print()
            print(
                "Final status: "
                "HUMAN_REVIEW_REQUIRED"
            )

            return result

        # -------------------------------------------------
        # 6. Execute the approved action.
        # -------------------------------------------------

        execution_result = execute_action(
            event,
            action,
        )

        contact_count += 1

        # Remember this intervention so it cannot
        # be selected again.
        tried_actions.append(action)

        print(
            f"Execution: "
            f"{execution_result['status']}"
        )

        # -------------------------------------------------
        # 7. Get actual simulated outcome.
        # -------------------------------------------------

        recovery_result = execute_recovery(
            outcomes=outcomes,
            event_id=event_id,
            action=action,
        )

        actual_status = recovery_result[
            "status"
        ]

        amount_recovered = float(
            recovery_result[
                "amount_recovered"
            ]
        )

        print(
            f"Actual outcome: "
            f"{actual_status}"
        )

        print(
            f"Amount recovered: "
            f"₹{amount_recovered:,.2f}"
        )

        # -------------------------------------------------
        # 8. Save attempt history.
        # -------------------------------------------------

        history.append(
            {
                "attempt": contact_count,
                "action": action,
                "predicted_probability":
                    recovery_probability,
                "expected_recovery":
                    expected_recovery,
                "actual_status":
                    actual_status,
                "amount_recovered":
                    amount_recovered,
            }
        )

        # -------------------------------------------------
        # 9. Recovery succeeded.
        # -------------------------------------------------

        if actual_status == "RECOVERED":

            result = {
                "event_id": event_id,
                "amount": event["amount"],
                "recommended_action": action,
                "recovery_probability": recovery_probability,
                "expected_recovery": expected_recovery,
                "contact_count": contact_count,
                "governor_decision": governor_decision,
                "governor_reason": governor_reason,
                "execution_status": execution_result[
                    "status"
                ],
                "actual_status": actual_status,
                "amount_recovered": amount_recovered,
                "final_status": "RECOVERED",
                "history": history,
            }

            write_audit_log(result)

            print()
            print(
                "Final status: RECOVERED"
            )

            return result

        print()
        print(
            "Recovery unsuccessful. "
            "Continuing..."
        )
        print()

    # -----------------------------------------------------
    # 10. Maximum attempts reached.
    # -----------------------------------------------------

    result = {
        "event_id": event_id,
        "amount": event["amount"],
        "recommended_action": history[-1][
            "action"
        ],
        "recovery_probability": history[-1][
            "predicted_probability"
        ],
        "expected_recovery": history[-1][
            "expected_recovery"
        ],
        "contact_count": contact_count,
        "governor_decision": "ESCALATE",
        "governor_reason": (
            "Maximum recovery attempts "
            "reached."
        ),
        "execution_status": "NOT_EXECUTED",
        "actual_status": "ESCALATED",
        "amount_recovered": 0.0,
        "final_status": "HUMAN_REVIEW_REQUIRED",
        "history": history,
    }

    write_audit_log(result)

    print()
    print(
        "Maximum attempts reached."
    )
    print(
        "Final status: "
        "HUMAN_REVIEW_REQUIRED"
    )

    return result


if __name__ == "__main__":

    model = load_model()

    outcomes = load_outcomes()

    events = pd.read_csv(
        "data/revenue_events.csv"
    )

    # E00005 is our deliberately selected
    # failure case for demonstrating
    # stateful multi-attempt recovery.
    event = events[
        events["event_id"] == "E00005"
    ].iloc[0].to_dict()

    result = run_agent(
        model=model,
        outcomes=outcomes,
        event=event,
    )

    print()
    print("Attempt history:")
    print("----------------")

    for attempt in result.get(
        "history",
        [],
    ):

        print(
            f"Attempt {attempt['attempt']}: "
            f"{attempt['action']} → "
            f"{attempt['actual_status']} "
            f"(₹{attempt['amount_recovered']:,.2f})"
        )