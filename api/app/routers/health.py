"""Health check router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from app.db import SessionLocal
from app.model_loader import model_metadata, get_model
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


def check_db() -> bool:
    """Check if database is reachable."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health endpoint for Kubernetes liveness/readiness probes."""
    db_ok = check_db()
    meta = model_metadata()
    model_ok = meta.get("loaded", False)

    if db_ok and model_ok:
        status = "healthy"
    elif not db_ok and not model_ok:
        status = "unhealthy"
    else:
        status = "degraded"

    return HealthResponse(
        status=status,
        db_connected=db_ok,
        model_loaded=model_ok,
        model_name=meta.get("name"),
        model_version=str(meta.get("version")),
        model_stage=meta.get("stage"),
    )


@router.get("/model-info")
async def model_info():
    """Detailed model information (useful for debugging which model is serving)."""
    meta = model_metadata()
    if not meta.get("loaded"):
        raise HTTPException(status_code=503, detail="No model loaded")
    return meta