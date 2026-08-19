"""Prediction router for predictive maintenance."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import SessionLocal, PredictionLog
from app.model_loader import get_model, model_metadata
from app.schemas import PredictRequest, PredictResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["prediction"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _risk_level(prob: float) -> str:
    if prob >= 0.7:
        return "critical"
    if prob >= 0.4:
        return "high"
    if prob >= 0.2:
        return "medium"
    return "low"


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Predict equipment failure probability within 30 days."""
    start = time.perf_counter()

    model = get_model()
    if model is None:
        logger.error("Prediction requested but no model loaded")
        raise HTTPException(status_code=503, detail="Model not loaded")

    meta = model_metadata()
    input_dict = request.model_dump()

    try:
        import pandas as pd
        df = pd.DataFrame([input_dict])

        proba = model.predict_proba(df)
        prob = float(proba[0][1])
        pred_label = "failure" if prob >= 0.5 else "no_failure"
    except Exception as exc:
        logger.exception("Prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    latency_ms = (time.perf_counter() - start) * 1000
    risk = _risk_level(prob)

    try:
        log = PredictionLog(
            input_payload=input_dict,
            prediction=pred_label,
            probability=prob,
            model_name=meta.get("name"),
            model_version=meta.get("version"),
            model_stage=meta.get("stage"),
            latency_ms=latency_ms,
        )
        db.add(log)
        db.commit()
    except Exception as exc:
        logger.warning("Failed to log prediction to DB: %s", exc)
        db.rollback()

    logger.info(
        "Prediction: %s (p=%.4f, risk=%s, latency=%.1fms, model=v%s/%s)",
        pred_label,
        prob,
        risk,
        latency_ms,
        meta.get("version"),
        meta.get("stage"),
    )

    return PredictResponse(
        prediction=pred_label,
        probability=prob,
        risk_level=risk,
        model_version=str(meta.get("version", "unknown")),
        model_stage=meta.get("stage", "unknown"),
    )
