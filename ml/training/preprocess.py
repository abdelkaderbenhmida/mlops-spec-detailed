# TODO: high - Add data validation before training
# TODO: medium - Implement hyperparameter logging
# TODO: low - Add model explainability integration
"""Data loading, validation and preprocessing for the predictive maintenance pipeline.

Real AI4I 2020 data: equipment_type (L/M/H), sensor readings, binary failure target.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import joblib
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yml")


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_raw(path: str | None = None) -> pd.DataFrame:
    config = load_config()
    path = path or config["data"]["raw_path"]
    df = pd.read_csv(path)
    logger.info("Loaded raw data: %s rows x %s cols from %s", len(df), len(df.columns), path)
    return df


def validate_schema(df: pd.DataFrame) -> None:
    config = load_config()
    target = config["data"]["target"]
    required = config["features"]["numeric"] + config["features"]["categorical"] + [target]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    logger.info("Schema validation passed")


def impute(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("unknown")
    return df


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    config = load_config()
    target = config["data"]["target"]
    df[target] = df[target].astype(int)
    return df


def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip().str.upper()
    return df


def load_and_preprocess(
    raw_path: str | None = None,
    config: dict[str, Any] | None = None,
    save_processed: str | None = None,
    save_encoders: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    config = config or load_config()
    raw_path = raw_path or config["data"]["raw_path"]
    test_size = config["data"]["test_size"]
    random_state = config["data"]["random_state"]
    target = config["data"]["target"]

    df = pd.read_csv(raw_path)
    validate_schema(df)
    df = normalize_categories(df)
    df = impute(df)
    df = encode_target(df)

    feature_cols = config["features"]["numeric"] + config["features"]["categorical"]
    X = df[feature_cols]
    y = df[target]

    encoders = {}
    for col in X.select_dtypes(include="object").columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        logger.info("Encoded categorical: %s -> %d classes", col, len(le.classes_))

    scaler = StandardScaler()
    numeric_cols = X.select_dtypes(include="number").columns.tolist()
    X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
    encoders["scaler"] = scaler
    encoders["numeric_cols"] = numeric_cols

    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y,
    )

    if save_processed:
        os.makedirs(os.path.dirname(save_processed), exist_ok=True)
        X_train.assign(**{target: y_train}).to_csv(save_processed, index=False)
        logger.info("Wrote processed train split -> %s", save_processed)

    if save_encoders:
        os.makedirs(os.path.dirname(save_encoders), exist_ok=True)
        joblib.dump(encoders, save_encoders)
        logger.info("Saved encoders -> %s", save_encoders)

    logger.info("Train=%d Test=%d", len(X_train), len(X_test))
    return X_train, X_test, y_train, y_test


def transform_new_data(df: pd.DataFrame, encoders_path: str) -> pd.DataFrame:
    encoders = joblib.load(encoders_path)
    df = df.copy()

    for col in df.select_dtypes(include="object").columns:
        if col in encoders and isinstance(encoders[col], LabelEncoder):
            le = encoders[col]
            df[col] = df[col].astype(str).map(lambda x: le.transform([x])[0] if x in le.classes_ else -1)

    numeric_cols = encoders.get("numeric_cols", [])
    if numeric_cols and "scaler" in encoders:
        df[numeric_cols] = encoders["scaler"].transform(df[numeric_cols])

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_and_preprocess()