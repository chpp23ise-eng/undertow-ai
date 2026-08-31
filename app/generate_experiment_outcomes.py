import pandas as pd

from recovery_simulator import simulate_recovery


TRAIN_EVENTS_PATH = "data/experiment_train_events.csv"
TEST_EVENTS_PATH = "data/experiment_test_events.csv"

TRAIN_OUTCOMES_PATH = "data/experiment_train_outcomes.csv"
TEST_OUTCOMES_PATH = "data/experiment_test_outcomes.csv"


def main():

    print("Loading experiment events...")
    print()

    train_events = pd.read_csv(
        TRAIN_EVENTS_PATH
    )

    test_events = pd.read_csv(
        TEST_EVENTS_PATH
    )

    print(
        f"Training events: {len(train_events)}"
    )

    print(
        f"Test events: {len(test_events)}"
    )

    print()

    # Generate outcomes independently.
    train_outcomes = simulate_recovery(
    train_events,
    seed=1000,)

    test_outcomes = simulate_recovery(
    test_events,
    seed=2000,)

    # Save them separately.
    train_outcomes.to_csv(
        TRAIN_OUTCOMES_PATH,
        index=False,
    )

    test_outcomes.to_csv(
        TEST_OUTCOMES_PATH,
        index=False,
    )

    print(
        f"Saved training outcomes to: "
        f"{TRAIN_OUTCOMES_PATH}"
    )

    print(
        f"Saved test outcomes to: "
        f"{TEST_OUTCOMES_PATH}"
    )

    print()
    print("Experiment outcome generation complete.")


if __name__ == "__main__":
    main()