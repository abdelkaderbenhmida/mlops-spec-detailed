#!/usr/bin/env python3
"""Train a RandomForest churn classifier and register it with MLflow.

Spec section 5:
  - mlflow.start_run(), fit model, mlflow.log_param() for hyperparams
  - mlflow.sklearn.log_model() for the raw pipeline (autologging-friendly)
  - mlflow.pyfunc.log_model() wrapping the pipeline so the serving layer can
    call mlflow.pyfunc.load_model() and get prediction + probability
  - register "churn-model" in the Model Registry and transition to Staging
"""

from __future__ import annotations

import logging
import os
import sys

import mlflow
import mlflow.pyfunc
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.pipeline import Pipeline

from features import build_preprocessor
from preprocess import load_and_preprocess, load_config

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class ChurnModelWrapper(mlflow.pyfunc.PythonModel):
    """pyfunc wrapper: maps the pipeline to (prediction, probability).

    The serving API calls mlflow.pyfunc.load_model() and then .predict(df);
    this wrapper returns a DataFrame with the exact response columns.
    """

    def __init__(self, pipeline: Pipeline) -> None:
        self.pipeline = pipeline

    def predict(self, context, model_input: pd.DataFrame) -> pd.DataFrame:
        proba = self.pipeline.predict_proba(model_input)[:, 1]
        prediction = (proba >= 0.5).astype(int)
        return pd.DataFrame(
            {
                "prediction": [
                    "churn" if p else "no_churn" for p in prediction
                ],
                "probability": proba,
            }
        )


def build_pipeline(config: dict) -> Pipeline:
    """Assemble preprocessor + RandomForestClassifier into one pipeline."""
    fconf = config["features"]
    mconf = config["model"]
    preprocessor = build_preprocessor(
        numeric=fconf["numeric"], categorical=fconf["categorical"]
    )
    classifier = RandomForestClassifier(
        n_estimators=mconf["n_estimators"],
        max_depth=mconf["max_depth"],
        min_samples_split=mconf["min_samples_split"],
        min_samples_leaf=mconf["min_samples_leaf"],
        max_features=mconf["max_features"],
        class_weight=mconf["class_weight"],
        n_jobs=mconf["n_jobs"],
        random_state=config["data"]["random_state"],
    )
    return Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", classifier)]
    )


def evaluate(pipeline: Pipeline, X_test, y_test) -> tuple[float, float]:
    """Return (f1, roc_auc) on the held-out test split."""
    proba = pipeline.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    f1 = f1_score(y_test, pred)
    auc = roc_auc_score(y_test, proba)
    return float(f1), float(auc)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    mflow = config["mlflow"]
    dconf = config["data"]

    mlflow.set_tracking_uri(mflow["tracking_uri"])
    mlflow.set_experiment(mflow["experiment_name"])

    X_train, X_test, y_train, y_test = load_and_preprocess(config=config)

    pipeline = build_pipeline(config)
    mconf = config["model"]

    with mlflow.start_run() as run:
        for key, value in mconf.items():
            mlflow.log_param(key, value)
        mlflow.log_params(
            {
                "test_size": dconf["test_size"],
                "random_state": dconf["random_state"],
            }
        )

        pipeline.fit(X_train, y_train)
        f1, auc = evaluate(pipeline, X_test, y_test)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("roc_auc", auc)

        # Log the raw sklearn pipeline (spec section 5).
        mlflow.sklearn.log_model(
            sk_model=pipeline,
            artifact_path="sklearn-model",
            input_example=X_test.head(1),
        )

        # Log the pyfunc wrapper that serves prediction + probability.
        mlflow.pyfunc.log_model(
            artifact_path=mflow["artifact_path"],
            python_model=ChurnModelWrapper(pipeline),
            input_example=X_test.head(1),
            signature=mlflow.models.infer_signature(
                X_test.head(1),
                ChurnModelWrapper(pipeline).predict(None, X_test.head(1)),
            ),
        )

        model_uri = f"runs:/{run.info.run_id}/{mflow['artifact_path']}"
        registered = mlflow.register_model(
            model_uri=model_uri, name=mflow["model_name"]
        )
        mlflow.tracking.MlflowClient().set_registered_model_tag(
            mflow["model_name"], "framework", "scikit-learn"
        )
        mlflow.tracking.MlflowClient().set_registered_model_tag(
            mflow["model_name"], "problem", "binary-classification"
        )

        # Automatic transition to Staging (Production stays a manual gate).
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=mflow["model_name"],
            version=registered.version,
            stage="Staging",
        )

        logger.info(
            "Registered %s version %s in Staging (run_id=%s, f1=%.4f, auc=%.4f)",
            mflow["model_name"],
            registered.version,
            run.info.run_id,
            f1,
            auc,
        )


if __name__ == "__main__":
    main()
