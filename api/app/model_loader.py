"""Model loader - loads the model from MLflow Model Registry on startup."""

from __future__ import annotations

import logging
import os
import threading

import mlflow.pyfunc

logger = logging.getLogger(__name__)

_model = None
_model_lock = threading.Lock()
_model_meta = {
    "loaded": False,
    "name": None,
    "version": None,
    "stage": None,
    "run_id": None,
}


def _tracking_uri() -> str:
    return os.getenv("MLFLOW_TRACKING_URI", "http://10.0.2.30:5000")


def _model_name() -> str:
    return os.getenv("MODEL_NAME", "maintenance-model")


def _model_stage() -> str:
    return os.getenv("MODEL_STAGE", "Staging")


def load_model() -> None:
    """Load the model from MLflow Model Registry by name + stage."""
    global _model, _model_meta

    tracking = _tracking_uri()
    name = _model_name()
    stage = _model_stage()

    logger.info("Loading model from MLflow: %s/%s (tracking: %s)", name, stage, tracking)

    try:
        mlflow.set_tracking_uri(tracking)
        model = mlflow.pyfunc.load_model(f"models:/{name}/{stage}")

        _model = model
        client = mlflow.tracking.MlflowClient()
        mv = client.get_latest_versions(name, stages=[stage])
        version = mv[0].version if mv else "unknown"
        run_id = mv[0].run_id if mv else "unknown"

        _model_meta = {
            "loaded": True,
            "name": name,
            "version": version,
            "stage": stage,
            "run_id": run_id,
        }
        logger.info(
            "Model loaded successfully: name=%s version=%s stage=%s run_id=%s",
            name,
            version,
            stage,
            run_id,
        )
    except Exception as exc:
        logger.exception("Failed to load model from MLflow: %s", exc)
        _model = None
        _model_meta = {
            "loaded": False,
            "name": name,
            "version": None,
            "stage": stage,
            "run_id": None,
        }


def get_model():
    """Return the loaded model (or None if not loaded)."""
    return _model


def model_metadata() -> dict:
    """Return metadata about the currently loaded model."""
    return _model_meta.copy()


def reload_model() -> None:
    """Admin-triggered reload (e.g., after a new model is promoted to Production)."""
    with _model_lock:
        load_model()
