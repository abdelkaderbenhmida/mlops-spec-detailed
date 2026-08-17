"""Shared pytest fixtures for the API test suite.

The tests run without any external dependency: MLflow, PostgreSQL and the
Prometheus scrape target are all stubbed out. That keeps the CI/CD ``test``
stage (``cicd/stages/test.sh``) runnable on the testing VM (VM12) before the
model has been promoted or the database has been provisioned.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import pytest

# The application is importable as ``app.*`` relative to the ``api/`` directory,
# which is what the container's WORKDIR is set to in docker/fastapi/Dockerfile.
API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


class FakeSession:
    """Minimal stand-in for a SQLAlchemy session.

    Records the objects that would have been persisted so tests can assert on
    prediction logging without a live PostgreSQL instance.
    """

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
    """Stub MLflow pyfunc model returning a fixed churn probability."""

    def __init__(self, probability: float = 0.83, prediction: str = "churn") -> None:
        self.probability = probability
        self.prediction = prediction
        self.last_input: Any = None

    def predict(self, df):
        import pandas as pd

        self.last_input = df
        return pd.DataFrame(
            {
                "prediction": [self.prediction] * len(df),
                "probability": [self.probability] * len(df),
            }
        )


LOADED_META: Dict[str, Any] = {
    "loaded": True,
    "name": "churn-model",
    "version": "7",
    "stage": "Production",
    "run_id": "0123456789abcdef0123456789abcdef",
}


@pytest.fixture
def fake_session() -> FakeSession:
    return FakeSession()


@pytest.fixture
def fake_model() -> FakeModel:
    return FakeModel()


@pytest.fixture
def app_module(monkeypatch):
    """Import ``main`` with the startup side effects neutralised."""
    import main as main_module

    monkeypatch.setattr(main_module, "init_db", lambda: None)
    monkeypatch.setattr(main_module, "load_model", lambda: None)
    return main_module


@pytest.fixture
def client(app_module, fake_model, fake_session, monkeypatch):
    """TestClient with a loaded model and a stubbed database."""
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
    """TestClient where the model failed to load (degraded / 503 paths)."""
    from fastapi.testclient import TestClient

    from app import model_loader
    from app.routers import health as health_router

    monkeypatch.setattr(model_loader, "_model", None)
    monkeypatch.setattr(
        model_loader,
        "_model_meta",
        {
            "loaded": False,
            "name": "churn-model",
            "version": None,
            "stage": "Production",
            "run_id": None,
        },
    )
    monkeypatch.setattr(health_router, "check_db", lambda: True)

    with TestClient(app_module.app) as test_client:
        yield test_client
    app_module.app.dependency_overrides.clear()


@pytest.fixture
def sample_payload() -> Dict[str, Any]:
    """A valid /predict body matching the spec section 6 contract."""
    return {
        "tenure_months": 12,
        "monthly_charges": 70.5,
        "total_charges": 846.0,
        "contract_type": "month-to-month",
        "payment_method": "electronic_check",
        "internet_service": "Fiber optic",
        "gender": "Female",
        "senior_citizen": 0,
        "partner": "No",
        "dependents": "No",
        "phone_service": "Yes",
        "multiple_lines": "No",
        "online_security": "No",
        "online_backup": "No",
        "device_protection": "No",
        "tech_support": "No",
        "streaming_tv": "No",
        "streaming_movies": "No",
        "paperless_billing": "Yes",
    }
