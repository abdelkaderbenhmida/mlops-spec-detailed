# API Documentation

> **Target platform per enterprise upgrade (Anvil).** The shipped lab code currently
> implements the older churn workload; this document describes the upgraded target.

The serving layer is a FastAPI application (`api/`) deployed as a Kubernetes `Deployment`
in the `mlops` namespace. A running instance also serves interactive OpenAPI docs at
`/docs` and ReDoc at `/redoc`; this document exists so the contract is readable without
one.

Base URL in the examples: `http://api.mlops.local` (the Ingress host). Locally:
`http://localhost:8000`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/predict` | Health/RUL scoring of one sensor window for one machine |
| `GET` | `/health` | Liveness/readiness probe — DB connectivity + model loaded |
| `GET` | `/model-info` | Which model version is actually serving |
| `POST` | `/reload-model` | Reload the Production model without a pod restart (admin) |
| `GET` | `/alerts` | List tiered alerts (Watch/Plan/Urgent/Stop) |
| `POST` | `/alerts/{id}/ack` | Acknowledge an alert |
| `GET` | `/metrics` | Prometheus exposition (scraped by VM09) |
| `GET` | `/docs`, `/redoc` | Interactive OpenAPI documentation |

---

## POST /predict

Runs the currently loaded `Production` model over one sensor window and logs the request
and result to TimescaleDB.

### Request

All sensor arrays must have equal length (the window the model was trained on); a
partially-filled payload is invalid — the model input is a fixed-length window, not a row
of independent columns.

| Field | Type | Constraint |
|---|---|---|
| `machine_id` | string | machine tag as mapped in `ml/ingest/tag_mapping.yml` (e.g. `P7`) |
| `window_start` | string (ISO-8601) | start timestamp of the window |
| `sensors.vibration_axial_mms` | array of float | 1 Hz × window length |
| `sensors.vibration_radial_mms` | array of float | 1 Hz × window length |
| `sensors.temperature_c` | array of float | 1 Hz × window length |
| `sensors.current_a` | array of float | 1 Hz × window length |
| `shaft_speed_rpm` | float | current shaft speed, used for bearing-frequency tracking |

```bash
curl -X POST http://api.mlops.local/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "machine_id": "P7",
    "window_start": "2026-08-01T00:00:00Z",
    "sensors": {
      "vibration_axial_mms": [2.1, 2.2],
      "vibration_radial_mms": [1.8, 1.9],
      "temperature_c": [63.1, 63.2],
      "current_a": [11.2, 11.2]
    },
    "shaft_speed_rpm": 1485
  }'
```

### Response `200`

```json
{
  "machine_id": "P7",
  "health_score": 0.82,
  "tier": "plan",
  "rul_days": { "lower": 9, "upper": 24, "confidence": 0.8 },
  "explanation": "Vibration at 142 Hz rose 3.4x over 21 days. That frequency corresponds to the outer-race defect frequency for this bearing at current shaft speed. Temperature is up 6C over the same period. Similar signatures on PUMP-3 (Mar 2025) and PUMP-11 (Sep 2025) preceded bearing failure by 12 and 19 days. Estimated remaining life: 9-24 days (80% confidence). Recommended: replace drive-end bearing at the next planned stop.",
  "model_version": "3",
  "model_stage": "Production"
}
```

| Field | Type | Meaning |
|---|---|---|
| `machine_id` | string | the machine the window belongs to |
| `health_score` | float 0–1 | Layer-1 reconstruction-error health index; 1 = known-healthy baseline, decreasing = degradation |
| `tier` | `watch` \| `plan` \| `urgent` \| `stop` | alert tier (the anomaly flag — anything above `watch` is an anomaly) |
| `rul_days` | object | Layer-2 remaining-useful-life distribution: `lower`, `upper` days, `confidence` 0–1 |
| `explanation` | string | explainability contract: operator-language text — frequencies, deltas, prior similar cases, recommendation |
| `model_version` | string | MLflow Registry version actually serving the request |
| `model_stage` | string | Registry stage, normally `Production` |

Tier conditions (main spec §7.2): `watch` = health index degrading, RUL > 30 days;
`plan` = RUL 7-30 days, confidence > 70%; `urgent` = RUL < 7 days or anomaly score
critical; `stop` = imminent catastrophic signature. Volume targets are commitments, not
estimates.

### Errors

| Status | When | Body |
|---|---|---|
| `422` | Request body fails validation (array length mismatch, missing sensor, bad enum) | FastAPI validation detail |
| `503` | No model is loaded (MLflow unreachable at startup, or no `Production` version) | `{"detail": "Model not loaded"}` |
| `500` | The model raised during inference (e.g. feature mismatch after a schema change) | `{"detail": "Prediction failed: ..."}` |

A failure to write the audit row to TimescaleDB does **not** fail the request: it is
logged as a warning, the transaction is rolled back, and the prediction is still
returned. The audit log is deliberately off the critical path.

### Side effects

Each call inserts one row into `predictions` on VM08:

```
id | machine_id | input_json (JSONB) | health_score | tier | rul_lower_days |
rul_upper_days | model_name | model_version | model_stage | latency_ms | created_at
```

---

## GET /health

Used as both the Kubernetes liveness and readiness probe.

```bash
curl http://api.mlops.local/health
```

```json
{
  "status": "healthy",
  "db_connected": true,
  "model_loaded": true,
  "model_name": "anvil-health",
  "model_version": "3",
  "model_stage": "Production"
}
```

`status` is derived from the two booleans:

| `db_connected` | `model_loaded` | `status` |
|---|---|---|
| true | true | `healthy` |
| true | false | `degraded` |
| false | true | `degraded` |
| false | false | `unhealthy` |

The endpoint always returns `200` — including when the service is unhealthy — so that
monitoring can distinguish "the pod is up but degraded" from "the pod is unreachable".
Probe configuration should treat anything other than `healthy` as not-ready.

---

## GET /model-info

Debugging endpoint: reports exactly which model the process has in memory. Useful when a
promotion appears not to have taken effect (the answer is usually that the pods were not
restarted).

```json
{
  "loaded": true,
  "name": "anvil-health",
  "version": "3",
  "stage": "Production",
  "run_id": "0123456789abcdef0123456789abcdef"
}
```

Returns `503` with `{"detail": "No model loaded"}` when no model is in memory.

---

## POST /reload-model

Admin endpoint: re-pulls `models:/anvil-health/Production` from MLflow and swaps it in
without a pod restart. Intended for the manual promotion flow; `kubectl rollout restart
deployment/inference -n mlops` also works but takes longer. Returns `503` when MLflow is
unreachable.

---

## GET /alerts / POST /alerts/{id}/ack

Read the tiered alerts produced by the alerting engine (`api/app/alerting.py`,
`kubernetes/alerting/`). Each alert carries the explanation object from `/predict` plus
`tier`, `machine_id`, `acked_by`, `acked_at` (rows in the `alerts` table on VM08).

- `GET /alerts` — list recent alerts; optional query filters (`tier`, `machine_id`,
  `unacked=true`).
- `POST /alerts/{id}/ack` — acknowledge an alert (the maintenance supervisor's side of
  the alert-trust loop). Returns `404` for an unknown alert id.

---

## GET /metrics

Prometheus exposition produced by `prometheus-fastapi-instrumentator`
(`api/app/metrics.py`). Notable series:

- `http_requests_total{method,handler,status}` — request counter; drives the request-rate
  and error-rate panels.
- `http_request_duration_seconds_bucket{handler,le}` — latency histogram; drives the
  p50/p95/p99 panels and the `InferenceHighLatency` alert.
- `http_requests_inprogress` — in-flight requests.
- `fastapi_model_loaded` — gauge, `1` when a model is loaded; drives the `NoModelLoaded`
  alert.

Tier distribution and health-score drift are read from the `predictions` table by the
Grafana Model Performance dashboard, not from `/metrics`. `/metrics` and `/health` are
excluded from the instrumentation so probe and scrape traffic does not distort the
latency histograms.

---

## Configuration

Supplied by `kubernetes/inference/configmap.yml` and `secret.yml`:

| Variable | Default | Purpose |
|---|---|---|
| `MLFLOW_TRACKING_URI` | `http://10.20.2.30:5000` | MLflow tracking/registry server (VM06) |
| `MODEL_NAME` | `anvil-health` | Registered model name |
| `MODEL_STAGE` | `Production` | Registry stage to load |
| `DB_HOST` | `10.20.2.40` | TimescaleDB host (VM08) |
| `DB_PORT` | `5432` | TimescaleDB port |
| `DB_NAME` | `mlops` | Application database |
| `DB_USER` | `mlops_app` | Application user |
| `DB_PASSWORD` | — | From `secret.yml`; never committed |

The image contains code only — the model is pulled from the local MLflow registry at pod
startup (`api/app/model_loader.py`). There is no external registry anywhere; everything
in the image comes from the VM12 mirror.

## Testing

`api/tests/` covers the whole contract without MLflow or TimescaleDB — the model and the
database session are stubbed in `api/tests/conftest.py`:

```bash
python3 -m pytest api/tests -q     # or: make test
```