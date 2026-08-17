#!/usr/bin/env python3
"""Evaluate the newest Staging model against the current Production model.

Spec section 5:
  - compute F1 and ROC-AUC on a held-out split
  - compare against the current "Production" model before allowing promotion
  - log metrics back to MLflow under the new run

Promotion rule (spec section 9 / docs/training-guide.md):
  the new model may be promoted only if its F1 is >= Production F1 - tolerance.
"""

from __future__ import annotations

import logging
import os
import sys

import mlflow
import mlflow.pyfunc
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ML_TRAINING_DIR = os.path.join(PROJECT_ROOT, "ml", "training")
if ML_TRAINING_DIR not in sys.path:
    sys.path.insert(0, ML_TRAINING_DIR)

from preprocess import load_and_preprocess, load_config


def _prediction_frame(model, X) -> tuple[list[str], list[float]]:
    """Predict using a pyfunc model that returns (prediction, probability)."""
    result = model.predict(X)
    if isinstance(result, pd.DataFrame):
        return list(result["prediction"]), list(result["probability"])
    raise ValueError(
        "Expected pyfunc model returning a DataFrame with "
        "'prediction'/'probability' columns, got %s" % type(result)
    )


def _metrics(X, y) -> tuple[float, float]:
    proba = pd.DataFrame({"p": 1.0}).reindex(index=[0])  # placeholder guard
    return 0.0, 0.0


def evaluate_model(model, X_test, y_test) -> dict:
    """Compute F1 and ROC-AUC for a loaded pyfunc model."""
    preds, probs = _prediction_frame(model, X_test)
    binary = [1 if p == "churn" else 0 for p in preds]
    f1 = f1_score(y_test, binary)
    auc = roc_auc_score(y_test, probs)
    return {"f1": float(f1), "roc_auc": float(auc)}


def load_registered(name: str, stage: str):
    """Load a model from the registry by name + stage (or return None)."""
    try:
        return mlflow.pyfunc.load_model(f"models:/{name}/{stage}")
    except Exception as exc:  # noqa: BLE001 - registry miss is a normal case
        logger.warning("No model at %s/%s: %s", name, stage, exc)
        return None


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    mflow = config["mlflow"]
    econf = config["evaluation"]

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", mflow["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(mflow["experiment_name"])

    _, X_test, _, y_test = load_and_preprocess(config=config)

    staging = load_registered(mflow["model_name"], "Staging")
    if staging is None:
        logger.error("No Staging model found; nothing to evaluate.")
        sys.exit(1)

    staging_metrics = evaluate_model(staging, X_test, y_test)
    logger.info(
        "Staging model: f1=%.4f roc_auc=%.4f",
        staging_metrics["f1"],
        staging_metrics["roc_auc"],
    )

    production = load_registered(mflow["model_name"], "Production")
    if production is None:
        logger.info("No Production model yet - Staging becomes the baseline.")
        promoted = True
        comparison = None
    else:
        prod_metrics = evaluate_model(production, X_test, y_test)
        comparison = prod_metrics
        threshold = prod_metrics["f1"] - econf["max_f1_regression"]
        promoted = staging_metrics["f1"] >= threshold
        logger.info(
            "Production model: f1=%.4f roc_auc=%.4f (promote if f1 >= %.4f) -> %s",
            prod_metrics["f1"],
            prod_metrics["roc_auc"],
            threshold,
            "PASS" if promoted else "FAIL",
        )

    with mlflow.start_run(run_name="evaluate-staging") as run:
        mlflow.log_metrics(
            {"staging_f1": staging_metrics["f1"], "staging_roc_auc": staging_metrics["roc_auc"]}
        )
        if comparison:
            mlflow.log_metrics(
                {"production_f1": comparison["f1"], "production_roc_auc": comparison["roc_auc"]}
            )
        mlflow.log_param("promotion_candidate", mflow["model_name"])
        mlflow.log_param("passes_threshold", promoted)

    print(
        f"EVALUATION f1={staging_metrics['f1']:.4f} "
        f"auc={staging_metrics['roc_auc']:.4f} "
        f"production={comparison['f1'] if comparison else 'N/A'} "
        f"promotable={promoted}"
    )
    sys.exit(0 if promoted else 2)


if __name__ == "__main__":
    main()
