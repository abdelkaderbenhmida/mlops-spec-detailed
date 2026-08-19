"""Tests for GET /health and GET /model-info (spec section 6)."""

from __future__ import annotations


def test_health_healthy_when_db_and_model_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["db_connected"] is True
    assert body["model_loaded"] is True
    assert body["model_name"] == "maintenance-model"
    assert body["model_version"] == "11"
    assert body["model_stage"] == "Staging"


def test_health_degraded_when_model_missing(client_no_model):
    response = client_no_model.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["db_connected"] is True
    assert body["model_loaded"] is False


def test_health_unhealthy_when_db_and_model_down(client_no_model, monkeypatch):
    from app.routers import health as health_router

    monkeypatch.setattr(health_router, "check_db", lambda: False)

    body = client_no_model.get("/health").json()
    assert body["status"] == "unhealthy"
    assert body["db_connected"] is False


def test_health_degraded_when_db_down_but_model_loaded(client, monkeypatch):
    from app.routers import health as health_router

    monkeypatch.setattr(health_router, "check_db", lambda: False)

    body = client.get("/health").json()
    assert body["status"] == "degraded"
    assert body["model_loaded"] is True


def test_check_db_returns_false_on_connection_error(monkeypatch):
    """The readiness probe must not raise when PostgreSQL is unreachable."""
    from app.routers import health as health_router

    def boom():
        raise RuntimeError("could not connect to server")

    monkeypatch.setattr(health_router, "SessionLocal", boom)
    assert health_router.check_db() is False


def test_model_info_returns_metadata(client):
    response = client.get("/model-info")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "maintenance-model"
    assert body["version"] == "11"
    assert body["stage"] == "Staging"
    assert body["run_id"]


def test_model_info_503_when_no_model(client_no_model):
    response = client_no_model.get("/model-info")

    assert response.status_code == 503
    assert response.json()["detail"] == "No model loaded"


def test_metrics_endpoint_exposed(client):
    """Prometheus scrape target from spec section 8 must be reachable."""
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_request" in response.text
