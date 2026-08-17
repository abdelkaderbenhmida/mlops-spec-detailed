"""Prediction router."""

from __future__ import annotations

import logging
import time
from uuid import uuid4

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


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Predict churn probability for a single customer."""
    start = time.perf_counter()

    model = get_model()
    if model is None:
        logger.error("Prediction requested but no model loaded")
        raise HTTPException(status_code=503, detail="Model not loaded")

    meta = model_metadata()
    input_dict = request.model_dump(by_alias=True)

    try:
        import pandas as pd
        df = pd.DataFrame([input_dict])
        result = model.predict(df)

        prob = float(result["probability"].iloc[0])
        pred = str(result["prediction"].iloc[0])
    except Exception as exc:
        logger.exception("Prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    latency_ms = (time.perf_counter() - start) * 1000

    # Log to PostgreSQL
    try:
        log = PredictionLog(
            id=uuid4().hex,
            input_payload=input_dict,
            prediction=pred,
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
        "Prediction: %s (p=%.4f, latency=%.1fms, model=v%s/%s)",
        pred,
        prob,
        latency_ms,
        meta.get("version"),
        meta.get("stage"),
    )

    return PredictResponse(
        prediction=pred,
        probability=prob,
        model_version=str(meta.get("version", "unknown")),
        model_stage=meta.get("stage", "unknown"),
    )