# TODO: high - Add data validation before training
# TODO: medium - Implement hyperparameter logging
# TODO: low - Add model explainability integration
"""Train a predictive maintenance model on real AI4I 2020 data and log it to MLflow.

Steps:
  1. Load maintenance.csv (real data)
  2. Preprocess (validate, impute, encode, scale, split)
  3. Train RandomForestClassifier with class_weight='balanced'
  4. Log params + metrics (F1, AUC, recall) to MLflow
  5. Register model as "maintenance-model"
"""

from __future__ import annotations

import logging
import os
import sys

import mlflow
import mlflow.xgboost
import numpy as np

from preprocess import load_and_preprocess, load_config

logger = logging.getLogger(__name__)

CONFIG = load_config()
MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME", CONFIG["mlflow"]["model_name"])


def train_and_log(
    raw_path: str | None = None,
    register: bool = True,
) -> dict:
    config = load_config()
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(config["mlflow"]["experiment_name"])

    X_train, X_test, y_train, y_test = load_and_preprocess(
        raw_path=raw_path,
        save_processed=config["data"]["processed_file"],
        save_encoders=config["data"]["encoders_file"],
    )

    import numpy as np
    from xgboost import XGBClassifier

    pos_weight = float(np.sum(y_train == 0) / max(np.sum(y_train == 1), 1))

    params = {
        "n_estimators": config["model"]["n_estimators"],
        "max_depth": config["model"]["max_depth"],
        "min_child_weight": 10,
        "colsample_bytree": 0.8,
        "scale_pos_weight": pos_weight,
        "random_state": 42,
        "n_jobs": config["model"]["n_jobs"],
        "device": "cuda",
        "tree_method": "hist",
    }
    from sklearn.metrics import (
        classification_report,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    clf = XGBClassifier(**params)
    clf.fit(X_train, y_train)

    proba = clf.predict_proba(X_test)[:, 1]
    preds = clf.predict(X_test)

    metrics = {
        "f1": float(f1_score(y_test, preds, zero_division=0)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
    }

    logger.info("F1=%.4f AUC=%.4f", metrics["f1"], metrics["roc_auc"])
    logger.info("\n%s", classification_report(y_test, preds, target_names=["No Failure", "Failure"], zero_division=0))

    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_params({
            "n_features": X_train.shape[1],
            "data_source": os.path.basename(raw_path or config["data"]["raw_path"]),
            "failure_rate": f"{y_train.mean():.4f}",
        })
        mlflow.log_metrics(metrics)
        mlflow.xgboost.log_model(clf, config["mlflow"]["artifact_path"])

        if register:
            model_uri = f"runs:/{run.info.run_id}/{config['mlflow']['artifact_path']}"
            registered = mlflow.register_model(model_uri, MODEL_NAME)
            client = mlflow.MlflowClient()
            client.transition_model_version_stage(
                name=MODEL_NAME, version=registered.version, stage="Staging"
            )
            logger.info("Registered %s v%s in Staging", MODEL_NAME, registered.version)

    return {"metrics": metrics, "run_id": run.info.run_id}


def main():
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-path", default=None)
    parser.add_argument("--register", action="store_true")
    args = parser.parse_args()

    try:
        result = train_and_log(raw_path=args.raw_path, register=args.register)
        print(f"Training done. F1={result['metrics']['f1']:.4f} AUC={result['metrics']['roc_auc']:.4f}")
    except Exception as e:
        logger.exception("Training failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()