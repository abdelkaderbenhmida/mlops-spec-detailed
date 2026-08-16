"""Data loading, validation and preprocessing for the churn pipeline.

Spec section 5:
  - schema check: expected columns, dtypes, null thresholds
  - imputation, encoding, stratified train/test split
"""

from __future__ import annotations

import logging
import os
from typing import Any

import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "customer_id",
    "gender",
    "senior_citizen",
    "partner",
    "dependents",
    "tenure",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "contract",
    "paperless_billing",
    "payment_method",
    "monthly_charges",
    "total_charges",
    "churn",
]

NUMERIC_COLUMNS = ["tenure", "monthly_charges", "total_charges"]

# Maximum tolerated missing ratio per column (%).
MAX_NULL_RATIO = 0.05

# Options that encode "no internet service" for add-on services.
NO_INTERNET_OPTIONS = ["No internet service", "No phone service"]


def load_config(config_path: str = "ml/training/config.yml") -> dict[str, Any]:
    """Load the pipeline configuration file."""
    with open(config_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def validate_schema(df: pd.DataFrame) -> None:
    """Fail loudly when the raw data does not match the expected schema."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    null_ratio = df.isnull().mean()
    bad = null_ratio[null_ratio > MAX_NULL_RATIO]
    if not bad.empty:
        raise ValueError(
            f"Columns exceed {MAX_NULL_RATIO:.0%} null threshold: "
            f"{dict(bad)}"
        )

    if df["churn"].nunique() < 2:
        raise ValueError("Target column 'churn' has fewer than 2 classes.")

    logger.info(
        "Schema OK: %d columns, %d rows, churn rate %.1f%%",
        df.shape[1],
        len(df),
        100 * (df["churn"] == "Yes").mean(),
    )


def impute(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing values: median for numerics, mode for categoricals."""
    out = df.copy()
    for col in NUMERIC_COLUMNS:
        if col in out.columns and out[col].isnull().any():
            median = pd.to_numeric(out[col], errors="coerce").median()
            out[col] = out[col].replace("", pd.NA)
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(median)
    for col in out.select_dtypes(include=["object"]).columns:
        if out[col].isnull().any():
            out[col] = out[col].fillna(out[col].mode().iloc[0])
    return out


def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse 'No internet service' / 'No phone service' to a shared code."""
    out = df.copy()
    for col in out.columns:
        if col in NO_INTERNET_OPTIONS:
            continue
        out[col] = out[col].replace(NO_INTERNET_OPTIONS, "No")
    # total_charges may contain empty strings in some exports.
    out["total_charges"] = pd.to_numeric(out["total_charges"], errors="coerce")
    return out


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """Map churn Yes/No to 1/0."""
    out = df.copy()
    out["churn"] = out["churn"].map({"Yes": 1, "No": 0})
    return out


def load_and_preprocess(
    raw_path: str | None = None,
    config: dict[str, Any] | None = None,
    save_processed: str | None = None,
) -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """Load the raw CSV, validate, clean and return stratified splits.

    Returns (X_train, X_test, y_train, y_test).
    """
    config = config or load_config()
    raw_path = raw_path or config["data"]["raw_path"]
    test_size = config["data"]["test_size"]
    random_state = config["data"]["random_state"]

    df = pd.read_csv(raw_path)
    validate_schema(df)
    df = normalize_categories(df)
    df = impute(df)
    df = encode_target(df)

    # Feature frame for training (drops id, keeps target out of X).
    X = df.drop(columns=["customer_id", "churn"])
    y = df["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    if save_processed:
        os.makedirs(os.path.dirname(save_processed), exist_ok=True)
        X_train.assign(churn=y_train).to_csv(save_processed, index=False)
        logger.info("Wrote processed train split -> %s", save_processed)

    logger.info(
        "Train=%d Test=%d (test_size=%.2f)",
        len(X_train),
        len(X_test),
        test_size,
    )
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cfg = load_config()
    X_tr, X_te, y_tr, y_te = load_and_preprocess(config=cfg)
    print(f"X_train: {X_tr.shape}, y_train positive: {int(y_tr.sum())}")
