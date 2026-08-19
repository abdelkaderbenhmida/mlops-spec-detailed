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

    clf = mlflow.sklearn.load_model(model_uri)

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