# TODO: medium - Add type hints where missing
# TODO: low - Add comprehensive docstring
# TODO: low - Add error handling for edge cases
"""Tests for POST /predict (predictive maintenance API)."""

from __future__ import annotations

import pytest


def test_predict_returns_spec_contract(client, sample_payload):
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"prediction", "probability", "risk_level", "model_version", "model_stage"}
    assert body["prediction"] in {"failure", "no_failure"}
    assert 0.0 <= body["probability"] <= 1.0
    assert body["risk_level"] in {"low", "medium", "high", "critical"}
    assert body["model_version"] == "11"
    assert body["model_stage"] == "Staging"


def test_predict_uses_loaded_model_probability(client, sample_payload, fake_model):
    fake_model.failure_prob = 0.42
    body = client.post("/predict", json=sample_payload).json()
    assert body["prediction"] == "no_failure"
    assert body["probability"] == pytest.approx(0.42)


def test_predict_passes_all_features_to_model(client, sample_payload, fake_model):
    client.post("/predict", json=sample_payload)
    frame = fake_model.last_input
    assert frame is not None
    assert len(frame) == 1
    assert "equipment_type" in frame.columns
    assert "sensor_temp" in frame.columns
    assert frame["sensor_temp"].iloc[0] != pytest.approx(70.0)
    assert frame.isna().sum().sum() == 0


def test_predict_applies_defaults_for_missing_fields(client, fake_model):
    response = client.post("/predict", json={})
    assert response.status_code == 200
    frame = fake_model.last_input
    assert "equipment_type" in frame.columns
    assert "age_months" in frame.columns
    assert frame.isna().sum().sum() == 0


def test_predict_logs_to_database(client, sample_payload, fake_session):
    client.post("/predict", json=sample_payload)
    assert fake_session.committed is True
    assert len(fake_session.added) == 1
    logged = fake_session.added[0]
    assert logged.prediction in {"failure", "no_failure"}
    assert 0.0 <= logged.probability <= 1.0
    assert logged.model_name == "maintenance-model"
    assert logged.model_version == "11"
    assert logged.model_stage == "Staging"
    assert logged.latency_ms >= 0


def test_predict_still_returns_200_when_db_logging_fails(client, sample_payload, fake_session):
    def boom(_obj):
        raise RuntimeError("connection pool exhausted")

    fake_session.add = boom
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    assert fake_session.rolled_back is True


def test_predict_503_when_no_model_loaded(client_no_model, sample_payload):
    response = client_no_model.post("/predict", json=sample_payload)
    assert response.status_code == 503
    assert response.json()["detail"] == "Model not loaded"


def test_predict_500_when_model_raises(client, sample_payload, fake_model):
    def boom(_df):
        raise ValueError("feature mismatch")
    fake_model.predict_proba = boom
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 500
    assert "Prediction failed" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {"age_months": -1},
        {"age_months": 500},
        {"sensor_vibration": -5},
        {"sensor_vibration": 100},
        {"equipment_type": "rocket"},
    ],
)
def test_predict_422_on_invalid_input(client, payload):
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_risk_levels(client, sample_payload, fake_model):
    for prob, expected in [(0.05, "low"), (0.25, "medium"), (0.5, "high"), (0.85, "critical")]:
        fake_model.failure_prob = prob
        body = client.post("/predict", json=sample_payload).json()
        assert body["risk_level"] == expected, f"prob={prob} -> {body['risk_level']}"
