# TODO: medium - Add type hints where missing
# TODO: low - Add comprehensive docstring
# TODO: low - Add error handling for edge cases
"""Shared pytest fixtures for the predictive maintenance API test suite."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pytest

API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


class FakeSession:
    def __init__(self) -> None:
        self.added: list[Any] = []
        self.committed = False
        self.rolled_back = False

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        pass


class FakeModel:
    """Stub model returning a fixed failure probability via predict_proba."""

    def __init__(self, failure_prob: float = 0.75) -> None:
        self.failure_prob = failure_prob
        self.last_input: Any = None

    def predict_proba(self, df):
        import pandas as pd
        self.last_input = df
        probs = np.array([[1 - self.failure_prob, self.failure_prob]] * len(df))
        return probs

    def predict(self, df):
        return (self.predict_proba(df)[:, 1] >= 0.5).astype(int)


LOADED_META: Dict[str, Any] = {
    "loaded": True,
    "name": "maintenance-model",
    "version": "11",
    "stage": "Staging",
    "run_id": "abcdef1234567890abcdef1234567890",
}


@pytest.fixture
def fake_session() -> FakeSession:
    return FakeSession()


@pytest.fixture
def fake_model() -> FakeModel:
    return FakeModel()


@pytest.fixture
def app_module(monkeypatch):
    import main as main_module
    monkeypatch.setattr(main_module, "init_db", lambda: None)
    monkeypatch.setattr(main_module, "load_model", lambda: None)
    return main_module


@pytest.fixture
def client(app_module, fake_model, fake_session, monkeypatch):
    from fastapi.testclient import TestClient
    from app import model_loader
    from app.routers import health as health_router
    from app.routers import predict as predict_router

    monkeypatch.setattr(model_loader, "_model", fake_model)
    monkeypatch.setattr(model_loader, "_model_meta", dict(LOADED_META))
    monkeypatch.setattr(health_router, "check_db", lambda: True)

    app_module.app.dependency_overrides[predict_router.get_db] = lambda: fake_session
    with TestClient(app_module.app) as test_client:
        yield test_client
    app_module.app.dependency_overrides.clear()


@pytest.fixture
def client_no_model(app_module, monkeypatch):
    from fastapi.testclient import TestClient
    from app import model_loader
    from app.routers import health as health_router

    monkeypatch.setattr(model_loader, "_model", None)
    monkeypatch.setattr(
        model_loader,
        "_model_meta",
        {"loaded": False, "name": "maintenance-model", "version": None, "stage": "Staging", "run_id": None},
    )
    monkeypatch.setattr(health_router, "check_db", lambda: True)

    with TestClient(app_module.app) as test_client:
        yield test_client
    app_module.app.dependency_overrides.clear()


@pytest.fixture
def sample_payload() -> Dict[str, Any]:
    return {
        "equipment_type": "pump",
        "age_months": 60,
        "operating_hours": 20000.0,
        "maintenance_history": 5,
        "sensor_temp": 70.0,
        "sensor_vibration": 1.0,
        "sensor_pressure": 35.0,
        "sensor_humidity": 50.0,
    }
