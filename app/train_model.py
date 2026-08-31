import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier


DATA_PATH = "data/training_data.csv"
MODEL_PATH = "models/recovery_model.joblib"


def load_data():
    """Load the training dataset."""

    return pd.read_csv(DATA_PATH)


def prepare_data(df):
    """
    Separate features from the target.

    The model must never see:
    - event_id
    - customer_id
    - hidden probabilities

    The target is 'recovered'.
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

    groups = df["event_id"]

    return X, y, groups


def build_model():
    """Build the preprocessing + XGBoost pipeline."""

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

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    return model


def main():

    print("Loading training data...")

    df = load_data()

    print(f"Total rows: {len(df)}")

    X, y, groups = prepare_data(df)

    # Split by event rather than individual rows.
    # This prevents the three interventions for the same
    # event from being split between train and test.
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42,
    )

    train_indices, test_indices = next(
        splitter.split(X, y, groups=groups)
    )

    X_train = X.iloc[train_indices]
    X_test = X.iloc[test_indices]

    y_train = y.iloc[train_indices]
    y_test = y.iloc[test_indices]

    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")
    print()

    print("Training XGBoost model...")

    model = build_model()

    model.fit(X_train, y_train)

    print("Training complete.")
    print()

    # Predictions
    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]

    # Evaluation
    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    auc = roc_auc_score(
        y_test,
        probabilities,
    )

    print("Model evaluation")
    print("----------------")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC-AUC:  {auc:.4f}")
    print()

    print("Classification report")
    print("---------------------")

    print(
        classification_report(
            y_test,
            predictions,
        )
    )

    # Save model
    os.makedirs("models", exist_ok=True)

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()