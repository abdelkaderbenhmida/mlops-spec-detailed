# TODO: high - Add quality gate with thresholds
# TODO: medium - Implement comparison vs current production model
# TODO: low - Add metrics export for Evidence Pack
"""Evaluate the predictive maintenance model on real AI4I 2020 data.

Loads the registered model from MLflow, computes AUC, F1, recall,
and gates on AUC >= 0.75, F1 >= 0.30 (real data is harder).
"""

from __future__ import annotations

import logging
import os
import sys

import mlflow
import numpy as np
from sklearn.metrics import classification_report, f1_score, roc_auc_score

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "training"))
from preprocess import load_and_preprocess, load_config

CONFIG = load_config()
MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME", CONFIG["mlflow"]["model_name"])
AUC_THRESHOLD = 0.75
F1_THRESHOLD = 0.30
MAX_F1_REGRESSION = float(CONFIG.get("evaluation", {}).get("max_f1_regression", 0.01))


def _production_f1(client, eval_model="Production"):
    """Fetch the currently deployed model's logged F1 (the bar the candidate
    must beat within tolerance). Returns None if no production model exists."""
    prod = client.get_latest_versions(MODEL_NAME, stages=[eval_model])
    if not prod:
        return None
    run = client.get_run(prod[0].run_id)
    f1 = run.data.metrics.get("f1_score") or run.data.metrics.get("f1")
    if f1 is None:
        return None
    return float(f1)


def main():
    logging.basicConfig(level=logging.INFO)

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", CONFIG["mlflow"]["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)

    client = mlflow.MlflowClient()
    versions = client.get_latest_versions(MODEL_NAME, stages=["Production", "Staging", "None"])
    if not versions:
        logger.error("No registered model found: %s", MODEL_NAME)
        sys.exit(1)

    version = versions[0]
    model_uri = f"models:/{MODEL_NAME}/{version.version}"
    logger.info("Evaluating %s v%s", MODEL_NAME, version.version)

    clf = mlflow.xgboost.load_model(model_uri)

    X_train, X_test, y_train, y_test = load_and_preprocess()

    proba = clf.predict_proba(X_test)[:, 1]
    preds = clf.predict(X_test)

    f1 = float(f1_score(y_test, preds, zero_division=0))
    auc = float(roc_auc_score(y_test, proba))
    recall = float(np.sum((preds == 1) & (y_test == 1)) / max(np.sum(y_test == 1), 1))

    print(classification_report(y_test, preds, target_names=["No Failure", "Failure"], zero_division=0))
    print(f"AUC:  {auc:.4f}  (threshold: {AUC_THRESHOLD})")
    print(f"F1:   {f1:.4f}  (threshold: {F1_THRESHOLD})")
    print(f"Recall: {recall:.4f}")

    # Regression gate vs current Production model (matches config.yml's
    # evaluation.max_f1_regression and the documented train.sh behavior).
    prod_f1 = _production_f1(client)
    if prod_f1 is not None:
        print(f"Production F1: {prod_f1:.4f}  (tolerance: {MAX_F1_REGRESSION})")
        if f1 < prod_f1 - MAX_F1_REGRESSION:
            print(
                f"FAIL: candidate F1 {f1:.4f} regressed >{MAX_F1_REGRESSION} "
                f"below production F1 {prod_f1:.4f}"
            )
            sys.exit(1)
    else:
        print("No Production model yet; skipping regression gate")

    if auc < AUC_THRESHOLD:
        print(f"FAIL: AUC {auc:.4f} < {AUC_THRESHOLD}")
        sys.exit(1)
    if f1 < F1_THRESHOLD:
        print(f"FAIL: F1 {f1:.4f} < {F1_THRESHOLD}")
        sys.exit(1)

    print(f"PASS: AUC={auc:.4f} >= {AUC_THRESHOLD}, F1={f1:.4f} >= {F1_THRESHOLD}")
    sys.exit(0)


if __name__ == "__main__":
    main()