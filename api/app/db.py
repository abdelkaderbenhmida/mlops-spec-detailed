"""PostgreSQL database layer for prediction logging.

Spec section 6/7: predictions table with columns:
id, input_payload JSONB, prediction, probability, model_name,
model_version, model_stage, latency_ms, created_at.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class PredictionLog(Base):
    """Prediction log table matching the spec schema."""

    __tablename__ = "predictions"

    id = Column(String(32), primary_key=True, default=lambda: uuid4().hex)
    input_payload = Column(JSONB, nullable=False)
    prediction = Column(String(50), nullable=False)
    probability = Column(Float, nullable=True)
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(20), nullable=True)
    model_stage = Column(String(20), nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_predictions_created_at", "created_at"),
        Index("ix_predictions_model_version", "model_version"),
    )


_engine = None
_SessionFactory = None


def _database_url() -> str:
    """Build the database URL from environment variables."""
    user = os.getenv("DB_USER", "mlops_app")
    password = os.getenv("DB_PASSWORD", "changeme_app")
    host = os.getenv("DB_HOST", "10.0.2.40")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "mlops")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def get_engine():
    """Get or create the SQLAlchemy engine (singleton)."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            _database_url(),
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    return _engine


def get_session_factory():
    """Get or create the session factory (singleton)."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine())
    return _SessionFactory


def SessionLocal():
    """Create a new session (for FastAPI dependency injection)."""
    return get_session_factory()()


def init_db() -> None:
    """Create tables if they don't exist."""
    try:
        Base.metadata.create_all(bind=get_engine())
        logger.info("Database tables initialized")
    except Exception as exc:
        logger.exception("Failed to initialize database: %s", exc)
        raise