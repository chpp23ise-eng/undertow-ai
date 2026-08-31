import json
import os

import pandas as pd


AUDIT_PATH = "data/audit_log.jsonl"
OUTPUT_PATH = "data/agent_metrics.json"


def load_audit_records():
    """Load all audit records from the JSONL audit log."""

    if not os.path.exists(AUDIT_PATH):
        return []

    records = []

    with open(
        AUDIT_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                records.append(
                    json.loads(line)
                )
            except json.JSONDecodeError:
                continue

    return records


def calculate_metrics(records):
    """Calculate operational metrics from agent runs."""

    if not records:
        return {
            "total_cases": 0,
            "recovered_cases": 0,
            "stopped_cases": 0,
            "escalated_cases": 0,
            "recovery_rate": 0.0,
            "total_amount_recovered": 0.0,
            "average_recovery": 0.0,
            "average_attempts": 0.0,
        }

    df = pd.DataFrame(records)

    total_cases = len(df)

    recovered_cases = (
        df["final_status"]
        == "RECOVERED"
    ).sum()

    stopped_cases = (
        df["final_status"]
        == "RECOVERY_STOPPED"
    ).sum()

    escalated_cases = (
        df["final_status"]
        == "HUMAN_REVIEW_REQUIRED"
    ).sum()

    total_amount_recovered = (
        pd.to_numeric(
            df["amount_recovered"],
            errors="coerce",
        )
        .fillna(0)
        .sum()
    )

    average_recovery = (
        total_amount_recovered
        / total_cases
        if total_cases > 0
        else 0.0
    )

    average_attempts = (
        pd.to_numeric(
            df["contact_count"],
            errors="coerce",
        )
        .fillna(0)
        .mean()
    )

    recovery_rate = (
        recovered_cases
        / total_cases
        if total_cases > 0
        else 0.0
    )

    return {
        "total_cases": int(
            total_cases
        ),
        "recovered_cases": int(
            recovered_cases
        ),
        "stopped_cases": int(
            stopped_cases
        ),
        "escalated_cases": int(
            escalated_cases
        ),
        "recovery_rate": float(
            recovery_rate
        ),
        "total_amount_recovered": float(
            total_amount_recovered
        ),
        "average_recovery": float(
            average_recovery
        ),
        "average_attempts": float(
            average_attempts
        ),
    }


def print_metrics(metrics):
    """Display metrics in a readable format."""

    print()
    print("UNDERTOW AGENT METRICS")
    print("======================")
    print()

    print(
        f"Total cases: "
        f"{metrics['total_cases']}"
    )

    print(
        f"Recovered cases: "
        f"{metrics['recovered_cases']}"
    )

    print(
        f"Stopped cases: "
        f"{metrics['stopped_cases']}"
    )

    print(
        f"Escalated cases: "
        f"{metrics['escalated_cases']}"
    )

    print()

    print(
        f"Recovery rate: "
        f"{metrics['recovery_rate']:.2%}"
    )

    print(
        f"Total amount recovered: "
        f"₹{metrics['total_amount_recovered']:,.2f}"
    )

    print(
        f"Average recovery per case: "
        f"₹{metrics['average_recovery']:,.2f}"
    )

    print(
        f"Average attempts: "
        f"{metrics['average_attempts']:.2f}"
    )


def main():

    print("Loading audit log...")

    records = load_audit_records()

    print(
        f"Audit records: {len(records)}"
    )

    metrics = calculate_metrics(
        records
    )

    print_metrics(metrics)

    # Save metrics for future dashboards
    # or API integration.
    os.makedirs(
        "data",
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2,
        )

    print()
    print(
        f"Metrics saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()