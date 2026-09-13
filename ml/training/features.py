# TODO: high - Add data validation before training
# TODO: medium - Implement hyperparameter logging
# TODO: low - Add model explainability integration
"""Feature engineering for the predictive maintenance pipeline.

Builds the sklearn feature preprocessor used both by training and evaluation.
The pipeline one-hot encodes categoricals (handle_unknown='ignore' so the
serving layer can send unseen values safely) and passes numerics through.
Column lists come from ml/training/config.yml (numeric + categorical); the
preprocessor is schema-agnostic.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logger = logging.getLogger(__name__)

DROP_COLUMNS = ["customer_id"]


def expected_columns(numeric: list[str], categorical: list[str]) -> list[str]:
    """Column names the serving API must send in each /predict payload."""
    return numeric + categorical


def drop_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove identifier columns not used as features."""
    drop = [c for c in DROP_COLUMNS if c in df.columns]
    if drop:
        logger.info("Dropping metadata columns: %s", drop)
    return df.drop(columns=drop)


def build_preprocessor(
    numeric: list[str], categorical: list[str], scale: bool = True
) -> ColumnTransformer:
    """ColumnTransformer: passthrough numerics, one-hot categoricals."""
    transformers: list[tuple[str, Any, list[str]]] = []

    numeric_present = [c for c in numeric if True]
    if numeric_present:
        steps = [("scaler", StandardScaler())] if scale else []
        transformers.append(
            (
                "num",
                Pipeline(steps) if steps else "passthrough",
                numeric_present,
            )
        )

    if categorical:
        transformers.append(
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical,
            )
        )

    if not transformers:
        raise ValueError("No features configured for the preprocessor.")

    return ColumnTransformer(transformers, remainder="drop")


def build_feature_columns(numeric: list[str], categorical: list[str]) -> list[str]:
    """Ordered feature columns expected by the trained model."""
    return numeric + categorical
