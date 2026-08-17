# API Documentation

The serving layer is a FastAPI application (`api/`) deployed as a Kubernetes `Deployment` in
the `mlops` namespace. A running instance also serves interactive OpenAPI docs at `/docs`
and ReDoc at `/redoc`; this document exists so the contract is readable without one.

Base URL in the examples: `http://api.mlops.local` (the Ingress host). Locally:
`http://localhost:8000`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/predict` | Churn prediction for one customer |
| `GET` | `/health` | Liveness/readiness probe — DB connectivity + model loaded |
| `GET` | `/model-info` | Which model version is actually serving |
| `GET` | `/metrics` | Prometheus exposition (scraped by VM09) |
| `GET` | `/docs`, `/redoc` | Interactive OpenAPI documentation |

---

## POST /predict

Runs the currently loaded `Production` model over a single customer record and logs the
request and result to PostgreSQL.

### Request

All fields are optional and have defaults, so a partial payload is valid. Two fields accept
an alias as well as their canonical name: `tenure_months` (alias `tenure`) and
`contract_type` (alias `contract`).

| Field | Type | Default | Constraint |
|---|---|---|---|
| `tenure_months` / `tenure` | int | `0` | 0–100 |
| `monthly_charges` | float | `50.0` | 0–200 |
| `total_charges` | float | `600.0` | >= 0 |
| `contract_type` / `contract` | enum | `month-to-month` | `month-to-month`, `one year`, `two year` |
| `payment_method` | enum | `electronic_check` | `electronic_check`, `mailed_check`, `bank_transfer`, `credit_card` |
| `internet_service` | enum | `Fiber optic` | `DSL`, `Fiber optic`, `No` |
| `gender` | enum | `Male` | `Male`, `Female` |
| `senior_citizen` | int | `0` | 0 or 1 |
| `partner` | enum | `No` | `Yes`, `No` |
| `dependents` | enum | `No` | `Yes`, `No` |
| `phone_service` | enum | `Yes` | `Yes`, `No` |
| `multiple_lines` | enum | `No` | `Yes`, `No`, `No phone service` |
| `online_security` | enum | `No` | `Yes`, `No`, `No internet service` |
| `online_backup` | enum | `No` | `Yes`, `No`, `No internet service` |
| `device_protection` | enum | `No` | `Yes`, `No`, `No internet service` |
| `tech_support` | enum | `No` | `Yes`, `No`, `No internet service` |
| `streaming_tv` | enum | `No` | `Yes`, `No`, `No internet service` |
| `streaming_movies` | enum | `No` | `Yes`, `No`, `No internet service` |
| `paperless_billing` | enum | `Yes` | `Yes`, `No` |

```bash
curl -X POST http://api.mlops.local/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "tenure_months": 12,
    "monthly_charges": 70.5,
    "total_charges": 846.0,
    "contract_type": "month-to-month",
    "payment_method": "electronic_check",
    "internet_service": "Fiber optic"
  }'
```

### Response `200`

```json
{
  "prediction": "churn",
  "probability": 0.83,
  "model_version": "7",
  "model_stage": "Production"
}
```

| Field | Type | Meaning |
|---|---|---|
| `prediction` | `"churn"` \| `"no_churn"` | Class at the 0.5 probability threshold |
| `probability` | float 0–1 | Probability of the positive (churn) class |
| `model_version` | string | MLflow Registry version actually serving the request |
| `model_stage` | string | Registry stage, normally `Production` |

### Errors

| Status | When | Body |
|---|---|---|
| `422` | Request body fails validation (out-of-range number, unknown enum value) | FastAPI validation detail |
| `503` | No model is loaded (MLflow unreachable at startup, or no `Production` version) | `{"detail": "Model not loaded"}` |
| `500` | The model raised during inference (e.g. feature mismatch after a schema change) | `{"detail": "Prediction failed: ..."}` |

A failure to write the audit row to PostgreSQL does **not** fail the request: it is logged as
a warning, the transaction is rolled back, and the prediction is still returned. The audit
log is deliberately off the critical path.

### Side effects

Each call inserts one row into `predictions` on VM08:

```
id | input_payload (JSONB) | prediction | probability | model_name |
model_version | model_stage | latency_ms | created_at
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
  "model_name": "churn-model",
  "model_version": "7",
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
monitoring can distinguish "the pod is up but degraded" from "the pod is unreachable". Probe
configuration should treat anything other than `healthy` as not-ready.

---

## GET /model-info

Debugging endpoint: reports exactly which model the process has in memory. Useful when a
promotion appears not to have taken effect (the answer is usually that the pods were not
restarted).

```json
{
  "loaded": true,
  "name": "churn-model",
  "version": "7",
  "stage": "Production",
  "run_id": "0123456789abcdef0123456789abcdef"
}
```

Returns `503` with `{"detail": "No model loaded"}` when no model is in memory.

---

## GET /metrics

Prometheus exposition produced by `prometheus-fastapi-instrumentator`
(`api/app/metrics.py`). Notable series:

- `http_requests_total{method,handler,status}` — request counter; drives the request-rate
  and error-rate panels.
- `http_request_duration_seconds_bucket{handler,le}` — latency histogram; drives the
  p50/p95/p99 panels and the `FastAPIHighLatency` alert.
- `http_requests_inprogress` — in-flight requests.
- `fastapi_model_loaded` — gauge, `1` when a model is loaded; drives the `NoModelLoaded`
  alert.

`/metrics` and `/health` are excluded from the instrumentation so probe and scrape traffic
does not distort the latency histograms.

---

## Configuration

Supplied by `kubernetes/fastapi/configmap.yml` and `secret.yml`:

| Variable | Default | Purpose |
|---|---|---|
| `MLFLOW_TRACKING_URI` | `http://10.0.2.30:5000` | MLflow tracking/registry server |
| `MODEL_NAME` | `churn-model` | Registered model name |
| `MODEL_STAGE` | `Production` | Registry stage to load |
| `DB_HOST` | `10.0.2.40` | PostgreSQL host (VM08) |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `mlops` | Application database |
| `DB_USER` | `mlops_app` | Application user |
| `DB_PASSWORD` | — | From `secret.yml`; never committed |

## Testing

`api/tests/` covers the whole contract without MLflow or PostgreSQL — the model and the
database session are stubbed in `api/tests/conftest.py`:

```bash
python3 -m pytest api/tests -q     # or: make test
```
