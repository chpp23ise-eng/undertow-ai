import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier


DATA_PATH = "data/experiment_training_data.csv"
MODEL_PATH = "models/recovery_model.joblib"


def load_data():
    """Load the experiment training dataset."""

    return pd.read_csv(DATA_PATH)


def prepare_data(df):
    """
    Separate features from the target.

    IDs and hidden simulator probabilities are excluded.

    The model learns from information available
    to Undertow at decision time.
    """

    features = [
        "amount",
        "event_type",
        "bank",
        "error_code",
        "product_id",
        "payment_method",
        "intervention",
    ]

    X = df[features]
    y = df["recovered"]

    return X, y


def build_model():
    """Build preprocessing + XGBoost pipeline."""

    numeric_features = [
        "amount",
    ]

    categorical_features = [
        "event_type",
        "bank",
        "error_code",
        "product_id",
        "payment_method",
        "intervention",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                "passthrough",
                numeric_features,
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
        ]
    )

    classifier = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def main():

    print("Loading experiment training data...")

    df = load_data()

    print(f"Training rows: {len(df)}")
    print()

    X, y = prepare_data(df)

    print("Training XGBoost model...")

    model = build_model()

    model.fit(
        X,
        y,
    )

    print("Training complete.")
    print()

    # Save model.
    os.makedirs(
        "models",
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(
        f"Model saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()