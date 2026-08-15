"""FastAPI application entrypoint.

Exposes:
- POST /predict
- GET /health
- GET /model-info

All prediction requests are logged to PostgreSQL.
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.db import init_db
from app.model_loader import load_model, model_metadata
from app.routers import health, predict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FastAPI application...")
    init_db()
    load_model()
    logger.info("Model loaded: %s", model_metadata())
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application...")


app = FastAPI(
    title="MLOps Churn Prediction API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(health.router)
app.include_router(predict.router)