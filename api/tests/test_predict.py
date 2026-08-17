"""Tests for POST /predict (spec section 6 contract + section 7 logging)."""

from __future__ import annotations

import pytest


def test_predict_returns_spec_contract(client, sample_payload):
    response = client.post("/predict", json=sample_payload)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"prediction", "probability", "model_version", "model_stage"}
    assert body["prediction"] in {"churn", "no_churn"}
    assert 0.0 <= body["probability"] <= 1.0
    assert body["model_version"] == "7"
    assert body["model_stage"] == "Production"


def test_predict_uses_loaded_model_probability(client, sample_payload, fake_model):
    fake_model.probability = 0.42
    fake_model.prediction = "no_churn"

    body = client.post("/predict", json=sample_payload).json()

    assert body["prediction"] == "no_churn"
    assert body["probability"] == pytest.approx(0.42)


def test_predict_passes_all_features_to_model(client, sample_payload, fake_model):
    client.post("/predict", json=sample_payload)

    frame = fake_model.last_input
    assert frame is not None
    assert len(frame) == 1
    # Serialised by alias, as the training pipeline expects.
    assert "tenure" in frame.columns
    assert "contract" in frame.columns
    assert frame["monthly_charges"].iloc[0] == pytest.approx(70.5)


def test_predict_accepts_alias_field_names(client, fake_model):
    """The schema declares aliases (tenure, contract); both spellings must work."""
    response = client.post(
        "/predict",
        json={"tenure": 3, "contract": "two year", "monthly_charges": 20.0},
    )

    assert response.status_code == 200
    assert fake_model.last_input["tenure"].iloc[0] == 3


def test_predict_applies_defaults_for_missing_fields(client, fake_model):
    response = client.post("/predict", json={})

    assert response.status_code == 200
    frame = fake_model.last_input
    assert frame["monthly_charges"].iloc[0] == pytest.approx(50.0)
    assert frame["contract"].iloc[0] == "month-to-month"


def test_predict_logs_to_database(client, sample_payload, fake_session):
    client.post("/predict", json=sample_payload)

    assert fake_session.committed is True
    assert len(fake_session.added) == 1

    logged = fake_session.added[0]
    assert logged.prediction in {"churn", "no_churn"}
    assert 0.0 <= logged.probability <= 1.0
    assert logged.model_name == "churn-model"
    assert logged.model_version == "7"
    assert logged.model_stage == "Production"
    assert logged.latency_ms >= 0
    assert logged.input_payload["monthly_charges"] == pytest.approx(70.5)


def test_predict_still_returns_200_when_db_logging_fails(client, sample_payload, fake_session):
    """A prediction must not fail because the audit log write failed."""

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

    fake_model.predict = boom

    response = client.post("/predict", json=sample_payload)

    assert response.status_code == 500
    assert "Prediction failed" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {"tenure_months": -1},
        {"tenure_months": 500},
        {"monthly_charges": -5},
        {"monthly_charges": 5000},
        {"senior_citizen": 2},
        {"contract_type": "lifetime"},
        {"internet_service": "satellite"},
    ],
)
def test_predict_422_on_invalid_input(client, payload):
    response = client.post("/predict", json=payload)

    assert response.status_code == 422
