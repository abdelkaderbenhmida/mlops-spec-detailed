"""Database layer for prediction logging (SQLite-compatible)."""

from __future__ import annotations

import logging
import os
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class PredictionLog(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    input_payload = Column(Text, nullable=False)
    prediction = Column(String(50), nullable=False)
    probability = Column(Float, nullable=True)
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(20), nullable=True)
    model_stage = Column(String(20), nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


_engine = None
_SessionFactory = None


def _database_url() -> str:
    sqlite_path = os.environ.get("SQLITE_DB", os.path.join(os.path.dirname(__file__), "..", "..", "predictions.db"))
    if os.getenv("DB_HOST"):
        user = os.getenv("DB_USER", "mlops_app")
        password = os.getenv("DB_PASSWORD", "changeme_app")
        host = os.getenv("DB_HOST", "10.0.2.40")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "mlops")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return f"sqlite:///{sqlite_path}"


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(_database_url(), pool_pre_ping=True)
    return _engine


def get_session_factory():
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine())
    return _SessionFactory


def SessionLocal():
    return get_session_factory()()


def init_db() -> None:
    try:
        Base.metadata.create_all(bind=get_engine())
        logger.info("Database tables initialized")
    except Exception as exc:
        logger.exception("Failed to initialize database: %s", exc)
        raise
