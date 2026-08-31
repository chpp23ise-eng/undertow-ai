import os

from data_generator import generate_data


TRAIN_EVENTS = 15000
TEST_EVENTS = 5000

TRAIN_PATH = "data/experiment_train_events.csv"
TEST_PATH = "data/experiment_test_events.csv"


def main():
    """
    Generate separate training and held-out
    evaluation datasets.
    """

    print("Generating experiment datasets...")
    print()

    train_df = generate_data(
        num_events=TRAIN_EVENTS,
        seed=100,
    )

    test_df = generate_data(
        num_events=TEST_EVENTS,
        seed=200,
    )

    os.makedirs(
        "data",
        exist_ok=True,
    )

    train_df.to_csv(
        TRAIN_PATH,
        index=False,
    )

    test_df.to_csv(
        TEST_PATH,
        index=False,
    )

    print(
        f"Training events: {len(train_df)}"
    )

    print(
        f"Saved to: {TRAIN_PATH}"
    )

    print()

    print(
        f"Held-out test events: {len(test_df)}"
    )

    print(
        f"Saved to: {TEST_PATH}"
    )

    print()

    print("Experiment split:")
    print("-----------------")
    print("Train → model learning")
    print("Test  → final evaluation")
    print()
    print(
        "The test events are completely "
        "separate from training events."
    )


if __name__ == "__main__":
    main()