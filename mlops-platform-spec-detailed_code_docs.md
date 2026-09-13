# mlops-platform-spec-detailed: generate-inventory.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/scripts/generate-inventory.py`
- **Total lines:** 81
- **File size:** 3200 bytes

## Line Type Summary
- **Code:** 64
- **Comment:** 1
- **Empty:** 13
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `#!/usr/bin/env python3`
> **Type:** Comment: !/usr/bin/env python3

### Line   2
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   3
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   4
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   5
> **Code:** `"""Generate the Ansible inventory from the static IP plan (spec sectio...`
> **Type:** Logical operation

### Line   6
> **Code:** ``
> **Type:** Empty line

### Line   7
> **Code:** `Output is written to stdout, suitable for:`
> **Type:** Logical operation

### Line   8
> **Code:** `python3 scripts/generate-inventory.py > ansible/inventory/hosts.ini`
> **Type:** Arithmetic operation

### Line   9
> **Code:** `"""`
> **Type:** Code statement

### Line  10
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `import sys`
> **Type:** Imports a module

### Line  13
> **Code:** `from typing import Dict, List`
> **Type:** Imports specific names from a module

### Line  14
> **Code:** ``
> **Type:** Empty line

### Line  15
> **Code:** `IP_PLAN: Dict[str, Dict[str, object]] = {`
> **Type:** Assignment/comparison

### Line  16
> **Code:** `"ctrl": {"hostname": "ctrl-node", "ip": "10.0.2.10", "groups": ["mgmt"...`
> **Type:** Arithmetic operation

### Line  17
> **Code:** `"git-cicd": {"hostname": "git-cicd", "ip": "10.0.2.11", "groups": ["mg...`
> **Type:** Arithmetic operation

### Line  18
> **Code:** `"k8s-cp": {"hostname": "k8s-cp", "ip": "10.0.2.20", "groups": ["k8s"]}...`
> **Type:** Arithmetic operation

### Line  19
> **Code:** `"k8s-wk1": {"hostname": "k8s-wk1", "ip": "10.0.2.21", "groups": ["k8s"...`
> **Type:** Arithmetic operation

### Line  20
> **Code:** `"k8s-wk2": {"hostname": "k8s-wk2", "ip": "10.0.2.22", "groups": ["k8s"...`
> **Type:** Arithmetic operation

### Line  21
> **Code:** `"mlflow": {"hostname": "mlflow", "ip": "10.0.2.30", "groups": ["ml_ser...`
> **Type:** Data structure operation

### Line  22
> **Code:** `"fastapi": {"hostname": "fastapi", "ip": "10.0.2.31", "groups": ["ml_s...`
> **Type:** Data structure operation

### Line  23
> **Code:** `"postgres": {"hostname": "postgres", "ip": "10.0.2.40", "groups": ["db...`
> **Type:** Data structure operation

### Line  24
> **Code:** `"prometheus": {"hostname": "prometheus", "ip": "10.0.2.50", "groups": ...`
> **Type:** Logical operation

### Line  25
> **Code:** `"grafana": {"hostname": "grafana", "ip": "10.0.2.51", "groups": ["moni...`
> **Type:** Logical operation

### Line  26
> **Code:** `"training-env": {"hostname": "training-env", "ip": "10.0.2.60", "group...`
> **Type:** Arithmetic operation

### Line  27
> **Code:** `"testing-env": {"hostname": "testing-env", "ip": "10.0.2.61", "groups"...`
> **Type:** Arithmetic operation

### Line  28
> **Code:** `}`
> **Type:** Code statement

### Line  29
> **Code:** ``
> **Type:** Empty line

### Line  30
> **Code:** `GROUPS: Dict[str, List[str]] = {`
> **Type:** Assignment/comparison

### Line  31
> **Code:** `"mgmt": ["ctrl-node", "git-cicd"],`
> **Type:** Arithmetic operation

### Line  32
> **Code:** `"k8s": ["k8s-cp", "k8s-wk1", "k8s-wk2"],`
> **Type:** Arithmetic operation

### Line  33
> **Code:** `"k8s_workers": ["k8s-wk1", "k8s-wk2"],`
> **Type:** Arithmetic operation

### Line  34
> **Code:** `"cicd": ["git-cicd"],`
> **Type:** Arithmetic operation

### Line  35
> **Code:** `"ml_servers": ["mlflow", "fastapi"],`
> **Type:** Data structure operation

### Line  36
> **Code:** `"db": ["postgres"],`
> **Type:** Data structure operation

### Line  37
> **Code:** `"monitoring": ["prometheus", "grafana"],`
> **Type:** Logical operation

### Line  38
> **Code:** `"training": ["training-env"],`
> **Type:** Arithmetic operation

### Line  39
> **Code:** `"testing": ["testing-env"],`
> **Type:** Arithmetic operation

### Line  40
> **Code:** `}`
> **Type:** Code statement

### Line  41
> **Code:** ``
> **Type:** Empty line

### Line  42
> **Code:** `DEFAULT_USER = "admin"`
> **Type:** Assignment/comparison

### Line  43
> **Code:** ``
> **Type:** Empty line

### Line  44
> **Code:** ``
> **Type:** Empty line

### Line  45
> **Code:** `def render(hosts: Dict[str, Dict[str, object]], groups: Dict[str, List...`
> **Type:** Function definition

### Line  46
> **Code:** `"""Render the inventory file content."""`
> **Type:** Logical operation

### Line  47
> **Code:** `lines: List[str] = []`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `lines.append("# Ansible inventory for the MLOps platform.")`
> **Type:** Logical operation

### Line  49
> **Code:** `lines.append("# Generated by scripts/generate-inventory.py from the IP...`
> **Type:** Arithmetic operation

### Line  50
> **Code:** `lines.append("# Private IPs are static on the 10.0.2.0/24 subnet; SSH ...`
> **Type:** Arithmetic operation

### Line  51
> **Code:** `lines.append("")`
> **Type:** Function call

### Line  52
> **Code:** `lines.append("[all:vars]")`
> **Type:** Function call

### Line  53
> **Code:** `lines.append(f"ansible_user = {user}")`
> **Type:** Assignment/comparison

### Line  54
> **Code:** `lines.append("ansible_become = true")`
> **Type:** Assignment/comparison

### Line  55
> **Code:** `lines.append("")`
> **Type:** Function call

### Line  56
> **Code:** ``
> **Type:** Empty line

### Line  57
> **Code:** `for name, meta in hosts.items():`
> **Type:** For loop

### Line  58
> **Code:** `lines.append(f"[{name}]")`
> **Type:** Function call

### Line  59
> **Code:** `lines.append(f"{meta['hostname']} ansible_host={meta['ip']}")`
> **Type:** Assignment/comparison

### Line  60
> **Code:** `lines.append("")`
> **Type:** Function call

### Line  61
> **Code:** ``
> **Type:** Empty line

### Line  62
> **Code:** `for group, members in groups.items():`
> **Type:** For loop

### Line  63
> **Code:** `lines.append(f"[{group}]")`
> **Type:** Function call

### Line  64
> **Code:** `for member in members:`
> **Type:** For loop

### Line  65
> **Code:** `lines.append(f"{member}")`
> **Type:** Function call

### Line  66
> **Code:** `lines.append("")`
> **Type:** Function call

### Line  67
> **Code:** `return "\n".join(lines)`
> **Type:** Returns a value from a function

### Line  68
> **Code:** ``
> **Type:** Empty line

### Line  69
> **Code:** ``
> **Type:** Empty line

### Line  70
> **Code:** `def main() -> int:`
> **Type:** Function definition

### Line  71
> **Code:** `inventory_user = DEFAULT_USER`
> **Type:** Assignment/comparison

### Line  72
> **Code:** `if "--user" in sys.argv:`
> **Type:** Conditional statement

### Line  73
> **Code:** `idx = sys.argv.index("--user")`
> **Type:** Assignment/comparison

### Line  74
> **Code:** `if idx + 1 < len(sys.argv):`
> **Type:** Conditional statement

### Line  75
> **Code:** `inventory_user = sys.argv[idx + 1]`
> **Type:** Assignment/comparison

### Line  76
> **Code:** `print(render(IP_PLAN, GROUPS, inventory_user))`
> **Type:** Prints output to console

### Line  77
> **Code:** `return 0`
> **Type:** Returns a value from a function

### Line  78
> **Code:** ``
> **Type:** Empty line

### Line  79
> **Code:** ``
> **Type:** Empty line

### Line  80
> **Code:** `if __name__ == "__main__":`
> **Type:** Conditional statement

### Line  81
> **Code:** `raise SystemExit(main())`
> **Type:** Raises an exception

## Summary
- **Total lines:** 81
- **Code lines:** 64
- **Comments:** 1
- **TODO items:** 3
- **Empty lines:** 13

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: generate-inventory.py*
---

# mlops-platform-spec-detailed: main.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/main.py`
- **Total lines:** 76
- **File size:** 1989 bytes

## Line Type Summary
- **Code:** 53
- **Comment:** 2
- **Empty:** 18
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: high - Add request validation and error handling`
> **Type:** TODO: high - Add request validation and error handling

### Line   2
> **Code:** `# TODO: medium - Implement request/response logging`
> **Type:** TODO: medium - Implement request/response logging

### Line   3
> **Code:** `# TODO: low - Add health check endpoint improvement`
> **Type:** TODO: low - Add health check endpoint improvement

### Line   4
> **Code:** `"""FastAPI application entrypoint.`
> **Type:** Code statement

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `Exposes:`
> **Type:** Code statement

### Line   7
> **Code:** `- POST /predict`
> **Type:** Arithmetic operation

### Line   8
> **Code:** `- GET /health`
> **Type:** Arithmetic operation

### Line   9
> **Code:** `- GET /model-info`
> **Type:** Arithmetic operation

### Line  10
> **Code:** ``
> **Type:** Empty line

### Line  11
> **Code:** `All prediction requests are logged to the predictions database.`
> **Type:** Code statement

### Line  12
> **Code:** `"""`
> **Type:** Code statement

### Line  13
> **Code:** ``
> **Type:** Empty line

### Line  14
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  15
> **Code:** ``
> **Type:** Empty line

### Line  16
> **Code:** `import logging`
> **Type:** Imports a module

### Line  17
> **Code:** `import time`
> **Type:** Imports a module

### Line  18
> **Code:** `from contextlib import asynccontextmanager`
> **Type:** Imports specific names from a module

### Line  19
> **Code:** ``
> **Type:** Empty line

### Line  20
> **Code:** `from fastapi import FastAPI, Request, Response`
> **Type:** Imports specific names from a module

### Line  21
> **Code:** `from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram,...`
> **Type:** Imports specific names from a module

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `from app.db import init_db`
> **Type:** Imports specific names from a module

### Line  24
> **Code:** `from app.model_loader import load_model, model_metadata`
> **Type:** Imports specific names from a module

### Line  25
> **Code:** `from app.routers import health, predict`
> **Type:** Imports specific names from a module

### Line  26
> **Code:** ``
> **Type:** Empty line

### Line  27
> **Code:** `logging.basicConfig(level=logging.INFO)`
> **Type:** Assignment/comparison

### Line  28
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  29
> **Code:** ``
> **Type:** Empty line

### Line  30
> **Code:** ``
> **Type:** Empty line

### Line  31
> **Code:** `@asynccontextmanager`
> **Type:** Code statement

### Line  32
> **Code:** `async def lifespan(app: FastAPI):`
> **Type:** Code statement

### Line  33
> **Code:** `# Startup`
> **Type:** Comment: Startup

### Line  34
> **Code:** `logger.info("Starting FastAPI application...")`
> **Type:** Function call

### Line  35
> **Code:** `init_db()`
> **Type:** Function call

### Line  36
> **Code:** `load_model()`
> **Type:** Function call

### Line  37
> **Code:** `logger.info("Model loaded: %s", model_metadata())`
> **Type:** Arithmetic operation

### Line  38
> **Code:** `yield`
> **Type:** Code statement

### Line  39
> **Code:** `# Shutdown`
> **Type:** Comment: Shutdown

### Line  40
> **Code:** `logger.info("Shutting down FastAPI application...")`
> **Type:** Function call

### Line  41
> **Code:** ``
> **Type:** Empty line

### Line  42
> **Code:** ``
> **Type:** Empty line

### Line  43
> **Code:** `app = FastAPI(`
> **Type:** Assignment/comparison

### Line  44
> **Code:** `title="MLOps Predictive Maintenance API",`
> **Type:** Assignment/comparison

### Line  45
> **Code:** `version="1.0.0",`
> **Type:** Assignment/comparison

### Line  46
> **Code:** `lifespan=lifespan,`
> **Type:** Assignment/comparison

### Line  47
> **Code:** `docs_url="/docs",`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `redoc_url="/redoc",`
> **Type:** Assignment/comparison

### Line  49
> **Code:** `)`
> **Type:** Code statement

### Line  50
> **Code:** ``
> **Type:** Empty line

### Line  51
> **Code:** `REQUEST_COUNT = Counter(`
> **Type:** Assignment/comparison

### Line  52
> **Code:** `"http_request_total", "Total HTTP requests", ["method", "path", "statu...`
> **Type:** Data structure operation

### Line  53
> **Code:** `)`
> **Type:** Code statement

### Line  54
> **Code:** `REQUEST_LATENCY = Histogram(`
> **Type:** Assignment/comparison

### Line  55
> **Code:** `"http_request_duration_seconds", "HTTP request latency", ["method", "p...`
> **Type:** Data structure operation

### Line  56
> **Code:** `)`
> **Type:** Code statement

### Line  57
> **Code:** ``
> **Type:** Empty line

### Line  58
> **Code:** ``
> **Type:** Empty line

### Line  59
> **Code:** `@app.middleware("http")`
> **Type:** Function call

### Line  60
> **Code:** `async def metrics_middleware(request: Request, call_next):`
> **Type:** Code statement

### Line  61
> **Code:** `start = time.perf_counter()`
> **Type:** Assignment/comparison

### Line  62
> **Code:** `response = await call_next(request)`
> **Type:** Assignment/comparison

### Line  63
> **Code:** `REQUEST_COUNT.labels(request.method, request.url.path, response.status...`
> **Type:** Function call

### Line  64
> **Code:** `REQUEST_LATENCY.labels(request.method, request.url.path).observe(`
> **Type:** Code statement

### Line  65
> **Code:** `time.perf_counter() - start`
> **Type:** Arithmetic operation

### Line  66
> **Code:** `)`
> **Type:** Code statement

### Line  67
> **Code:** `return response`
> **Type:** Returns a value from a function

### Line  68
> **Code:** ``
> **Type:** Empty line

### Line  69
> **Code:** ``
> **Type:** Empty line

### Line  70
> **Code:** `@app.get("/metrics")`
> **Type:** Arithmetic operation

### Line  71
> **Code:** `async def metrics():`
> **Type:** Code statement

### Line  72
> **Code:** `return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)`
> **Type:** Returns a value from a function

### Line  73
> **Code:** ``
> **Type:** Empty line

### Line  74
> **Code:** ``
> **Type:** Empty line

### Line  75
> **Code:** `app.include_router(health.router)`
> **Type:** Function call

### Line  76
> **Code:** `app.include_router(predict.router)`
> **Type:** Function call

## Summary
- **Total lines:** 76
- **Code lines:** 53
- **Comments:** 2
- **TODO items:** 3
- **Empty lines:** 18

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: main.py*
---

# mlops-platform-spec-detailed: test_predict.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/tests/test_predict.py`
- **Total lines:** 105
- **File size:** 3910 bytes

## Line Type Summary
- **Code:** 79
- **Comment:** 0
- **Empty:** 23
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Tests for POST /predict (predictive maintenance API)."""`
> **Type:** Arithmetic operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line   7
> **Code:** ``
> **Type:** Empty line

### Line   8
> **Code:** `import pytest`
> **Type:** Imports a module

### Line   9
> **Code:** ``
> **Type:** Empty line

### Line  10
> **Code:** ``
> **Type:** Empty line

### Line  11
> **Code:** `def test_predict_returns_spec_contract(client, sample_payload):`
> **Type:** Function definition

### Line  12
> **Code:** `response = client.post("/predict", json=sample_payload)`
> **Type:** Assignment/comparison

### Line  13
> **Code:** `assert response.status_code == 200`
> **Type:** Enforces a condition

### Line  14
> **Code:** `body = response.json()`
> **Type:** Assignment/comparison

### Line  15
> **Code:** `assert set(body) == {"prediction", "probability", "risk_level", "model...`
> **Type:** Enforces a condition

### Line  16
> **Code:** `assert body["prediction"] in {"failure", "no_failure"}`
> **Type:** Enforces a condition

### Line  17
> **Code:** `assert 0.0 <= body["probability"] <= 1.0`
> **Type:** Enforces a condition

### Line  18
> **Code:** `assert body["risk_level"] in {"low", "medium", "high", "critical"}`
> **Type:** Enforces a condition

### Line  19
> **Code:** `assert body["model_version"] == "11"`
> **Type:** Enforces a condition

### Line  20
> **Code:** `assert body["model_stage"] == "Staging"`
> **Type:** Enforces a condition

### Line  21
> **Code:** ``
> **Type:** Empty line

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `def test_predict_uses_loaded_model_probability(client, sample_payload,...`
> **Type:** Function definition

### Line  24
> **Code:** `fake_model.failure_prob = 0.42`
> **Type:** Assignment/comparison

### Line  25
> **Code:** `body = client.post("/predict", json=sample_payload).json()`
> **Type:** Assignment/comparison

### Line  26
> **Code:** `assert body["prediction"] == "no_failure"`
> **Type:** Enforces a condition

### Line  27
> **Code:** `assert body["probability"] == pytest.approx(0.42)`
> **Type:** Enforces a condition

### Line  28
> **Code:** ``
> **Type:** Empty line

### Line  29
> **Code:** ``
> **Type:** Empty line

### Line  30
> **Code:** `def test_predict_passes_all_features_to_model(client, sample_payload, ...`
> **Type:** Function definition

### Line  31
> **Code:** `client.post("/predict", json=sample_payload)`
> **Type:** Assignment/comparison

### Line  32
> **Code:** `frame = fake_model.last_input`
> **Type:** Assignment/comparison

### Line  33
> **Code:** `assert frame is not None`
> **Type:** Enforces a condition

### Line  34
> **Code:** `assert len(frame) == 1`
> **Type:** Enforces a condition

### Line  35
> **Code:** `assert "equipment_type" in frame.columns`
> **Type:** Enforces a condition

### Line  36
> **Code:** `assert "sensor_temp" in frame.columns`
> **Type:** Enforces a condition

### Line  37
> **Code:** `assert frame["sensor_temp"].iloc[0] == pytest.approx(70.0)`
> **Type:** Enforces a condition

### Line  38
> **Code:** ``
> **Type:** Empty line

### Line  39
> **Code:** ``
> **Type:** Empty line

### Line  40
> **Code:** `def test_predict_applies_defaults_for_missing_fields(client, fake_mode...`
> **Type:** Function definition

### Line  41
> **Code:** `response = client.post("/predict", json={})`
> **Type:** Assignment/comparison

### Line  42
> **Code:** `assert response.status_code == 200`
> **Type:** Enforces a condition

### Line  43
> **Code:** `frame = fake_model.last_input`
> **Type:** Assignment/comparison

### Line  44
> **Code:** `assert frame["equipment_type"].iloc[0] == "pump"`
> **Type:** Enforces a condition

### Line  45
> **Code:** `assert frame["age_months"].iloc[0] == 60`
> **Type:** Enforces a condition

### Line  46
> **Code:** ``
> **Type:** Empty line

### Line  47
> **Code:** ``
> **Type:** Empty line

### Line  48
> **Code:** `def test_predict_logs_to_database(client, sample_payload, fake_session...`
> **Type:** Function definition

### Line  49
> **Code:** `client.post("/predict", json=sample_payload)`
> **Type:** Assignment/comparison

### Line  50
> **Code:** `assert fake_session.committed is True`
> **Type:** Enforces a condition

### Line  51
> **Code:** `assert len(fake_session.added) == 1`
> **Type:** Enforces a condition

### Line  52
> **Code:** `logged = fake_session.added[0]`
> **Type:** Assignment/comparison

### Line  53
> **Code:** `assert logged.prediction in {"failure", "no_failure"}`
> **Type:** Enforces a condition

### Line  54
> **Code:** `assert 0.0 <= logged.probability <= 1.0`
> **Type:** Enforces a condition

### Line  55
> **Code:** `assert logged.model_name == "maintenance-model"`
> **Type:** Enforces a condition

### Line  56
> **Code:** `assert logged.model_version == "11"`
> **Type:** Enforces a condition

### Line  57
> **Code:** `assert logged.model_stage == "Staging"`
> **Type:** Enforces a condition

### Line  58
> **Code:** `assert logged.latency_ms >= 0`
> **Type:** Enforces a condition

### Line  59
> **Code:** ``
> **Type:** Empty line

### Line  60
> **Code:** ``
> **Type:** Empty line

### Line  61
> **Code:** `def test_predict_still_returns_200_when_db_logging_fails(client, sampl...`
> **Type:** Function definition

### Line  62
> **Code:** `def boom(_obj):`
> **Type:** Function definition

### Line  63
> **Code:** `raise RuntimeError("connection pool exhausted")`
> **Type:** Raises an exception

### Line  64
> **Code:** ``
> **Type:** Empty line

### Line  65
> **Code:** `fake_session.add = boom`
> **Type:** Assignment/comparison

### Line  66
> **Code:** `response = client.post("/predict", json=sample_payload)`
> **Type:** Assignment/comparison

### Line  67
> **Code:** `assert response.status_code == 200`
> **Type:** Enforces a condition

### Line  68
> **Code:** `assert fake_session.rolled_back is True`
> **Type:** Enforces a condition

### Line  69
> **Code:** ``
> **Type:** Empty line

### Line  70
> **Code:** ``
> **Type:** Empty line

### Line  71
> **Code:** `def test_predict_503_when_no_model_loaded(client_no_model, sample_payl...`
> **Type:** Function definition

### Line  72
> **Code:** `response = client_no_model.post("/predict", json=sample_payload)`
> **Type:** Assignment/comparison

### Line  73
> **Code:** `assert response.status_code == 503`
> **Type:** Enforces a condition

### Line  74
> **Code:** `assert response.json()["detail"] == "Model not loaded"`
> **Type:** Enforces a condition

### Line  75
> **Code:** ``
> **Type:** Empty line

### Line  76
> **Code:** ``
> **Type:** Empty line

### Line  77
> **Code:** `def test_predict_500_when_model_raises(client, sample_payload, fake_mo...`
> **Type:** Function definition

### Line  78
> **Code:** `def boom(_df):`
> **Type:** Function definition

### Line  79
> **Code:** `raise ValueError("feature mismatch")`
> **Type:** Raises an exception

### Line  80
> **Code:** `fake_model.predict_proba = boom`
> **Type:** Assignment/comparison

### Line  81
> **Code:** `response = client.post("/predict", json=sample_payload)`
> **Type:** Assignment/comparison

### Line  82
> **Code:** `assert response.status_code == 500`
> **Type:** Enforces a condition

### Line  83
> **Code:** `assert "Prediction failed" in response.json()["detail"]`
> **Type:** Enforces a condition

### Line  84
> **Code:** ``
> **Type:** Empty line

### Line  85
> **Code:** ``
> **Type:** Empty line

### Line  86
> **Code:** `@pytest.mark.parametrize(`
> **Type:** Code statement

### Line  87
> **Code:** `"payload",`
> **Type:** Code statement

### Line  88
> **Code:** `[`
> **Type:** Code statement

### Line  89
> **Code:** `{"age_months": -1},`
> **Type:** Arithmetic operation

### Line  90
> **Code:** `{"age_months": 500},`
> **Type:** Data structure operation

### Line  91
> **Code:** `{"sensor_vibration": -5},`
> **Type:** Arithmetic operation

### Line  92
> **Code:** `{"sensor_vibration": 100},`
> **Type:** Logical operation

### Line  93
> **Code:** `{"equipment_type": "rocket"},`
> **Type:** Data structure operation

### Line  94
> **Code:** `],`
> **Type:** Code statement

### Line  95
> **Code:** `)`
> **Type:** Code statement

### Line  96
> **Code:** `def test_predict_422_on_invalid_input(client, payload):`
> **Type:** Function definition

### Line  97
> **Code:** `response = client.post("/predict", json=payload)`
> **Type:** Assignment/comparison

### Line  98
> **Code:** `assert response.status_code == 422`
> **Type:** Enforces a condition

### Line  99
> **Code:** ``
> **Type:** Empty line

### Line 100
> **Code:** ``
> **Type:** Empty line

### Line 101
> **Code:** `def test_risk_levels(client, sample_payload, fake_model):`
> **Type:** Function definition

### Line 102
> **Code:** `for prob, expected in [(0.05, "low"), (0.25, "medium"), (0.5, "high"),...`
> **Type:** For loop

### Line 103
> **Code:** `fake_model.failure_prob = prob`
> **Type:** Assignment/comparison

### Line 104
> **Code:** `body = client.post("/predict", json=sample_payload).json()`
> **Type:** Assignment/comparison

### Line 105
> **Code:** `assert body["risk_level"] == expected, f"prob={prob} -> {body['risk_le...`
> **Type:** Enforces a condition

## Summary
- **Total lines:** 105
- **Code lines:** 79
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 23

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: test_predict.py*
---

# mlops-platform-spec-detailed: test_health.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/tests/test_health.py`
- **Total lines:** 86
- **File size:** 2732 bytes

## Line Type Summary
- **Code:** 55
- **Comment:** 0
- **Empty:** 28
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Tests for GET /health and GET /model-info (spec section 6)."""`
> **Type:** Arithmetic operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line   7
> **Code:** ``
> **Type:** Empty line

### Line   8
> **Code:** ``
> **Type:** Empty line

### Line   9
> **Code:** `def test_health_healthy_when_db_and_model_ok(client):`
> **Type:** Function definition

### Line  10
> **Code:** `response = client.get("/health")`
> **Type:** Assignment/comparison

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `assert response.status_code == 200`
> **Type:** Enforces a condition

### Line  13
> **Code:** `body = response.json()`
> **Type:** Assignment/comparison

### Line  14
> **Code:** `assert body["status"] == "healthy"`
> **Type:** Enforces a condition

### Line  15
> **Code:** `assert body["db_connected"] is True`
> **Type:** Enforces a condition

### Line  16
> **Code:** `assert body["model_loaded"] is True`
> **Type:** Enforces a condition

### Line  17
> **Code:** `assert body["model_name"] == "maintenance-model"`
> **Type:** Enforces a condition

### Line  18
> **Code:** `assert body["model_version"] == "11"`
> **Type:** Enforces a condition

### Line  19
> **Code:** `assert body["model_stage"] == "Staging"`
> **Type:** Enforces a condition

### Line  20
> **Code:** ``
> **Type:** Empty line

### Line  21
> **Code:** ``
> **Type:** Empty line

### Line  22
> **Code:** `def test_health_degraded_when_model_missing(client_no_model):`
> **Type:** Function definition

### Line  23
> **Code:** `response = client_no_model.get("/health")`
> **Type:** Assignment/comparison

### Line  24
> **Code:** ``
> **Type:** Empty line

### Line  25
> **Code:** `assert response.status_code == 200`
> **Type:** Enforces a condition

### Line  26
> **Code:** `body = response.json()`
> **Type:** Assignment/comparison

### Line  27
> **Code:** `assert body["status"] == "degraded"`
> **Type:** Enforces a condition

### Line  28
> **Code:** `assert body["db_connected"] is True`
> **Type:** Enforces a condition

### Line  29
> **Code:** `assert body["model_loaded"] is False`
> **Type:** Enforces a condition

### Line  30
> **Code:** ``
> **Type:** Empty line

### Line  31
> **Code:** ``
> **Type:** Empty line

### Line  32
> **Code:** `def test_health_unhealthy_when_db_and_model_down(client_no_model, monk...`
> **Type:** Function definition

### Line  33
> **Code:** `from app.routers import health as health_router`
> **Type:** Imports specific names from a module

### Line  34
> **Code:** ``
> **Type:** Empty line

### Line  35
> **Code:** `monkeypatch.setattr(health_router, "check_db", lambda: False)`
> **Type:** Function call

### Line  36
> **Code:** ``
> **Type:** Empty line

### Line  37
> **Code:** `body = client_no_model.get("/health").json()`
> **Type:** Assignment/comparison

### Line  38
> **Code:** `assert body["status"] == "unhealthy"`
> **Type:** Enforces a condition

### Line  39
> **Code:** `assert body["db_connected"] is False`
> **Type:** Enforces a condition

### Line  40
> **Code:** ``
> **Type:** Empty line

### Line  41
> **Code:** ``
> **Type:** Empty line

### Line  42
> **Code:** `def test_health_degraded_when_db_down_but_model_loaded(client, monkeyp...`
> **Type:** Function definition

### Line  43
> **Code:** `from app.routers import health as health_router`
> **Type:** Imports specific names from a module

### Line  44
> **Code:** ``
> **Type:** Empty line

### Line  45
> **Code:** `monkeypatch.setattr(health_router, "check_db", lambda: False)`
> **Type:** Function call

### Line  46
> **Code:** ``
> **Type:** Empty line

### Line  47
> **Code:** `body = client.get("/health").json()`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `assert body["status"] == "degraded"`
> **Type:** Enforces a condition

### Line  49
> **Code:** `assert body["model_loaded"] is True`
> **Type:** Enforces a condition

### Line  50
> **Code:** ``
> **Type:** Empty line

### Line  51
> **Code:** ``
> **Type:** Empty line

### Line  52
> **Code:** `def test_check_db_returns_false_on_connection_error(monkeypatch):`
> **Type:** Function definition

### Line  53
> **Code:** `"""The readiness probe must not raise when PostgreSQL is unreachable."...`
> **Type:** Logical operation

### Line  54
> **Code:** `from app.routers import health as health_router`
> **Type:** Imports specific names from a module

### Line  55
> **Code:** ``
> **Type:** Empty line

### Line  56
> **Code:** `def boom():`
> **Type:** Function definition

### Line  57
> **Code:** `raise RuntimeError("could not connect to server")`
> **Type:** Raises an exception

### Line  58
> **Code:** ``
> **Type:** Empty line

### Line  59
> **Code:** `monkeypatch.setattr(health_router, "SessionLocal", boom)`
> **Type:** Function call

### Line  60
> **Code:** `assert health_router.check_db() is False`
> **Type:** Enforces a condition

### Line  61
> **Code:** ``
> **Type:** Empty line

### Line  62
> **Code:** ``
> **Type:** Empty line

### Line  63
> **Code:** `def test_model_info_returns_metadata(client):`
> **Type:** Function definition

### Line  64
> **Code:** `response = client.get("/model-info")`
> **Type:** Assignment/comparison

### Line  65
> **Code:** ``
> **Type:** Empty line

### Line  66
> **Code:** `assert response.status_code == 200`
> **Type:** Enforces a condition

### Line  67
> **Code:** `body = response.json()`
> **Type:** Assignment/comparison

### Line  68
> **Code:** `assert body["name"] == "maintenance-model"`
> **Type:** Enforces a condition

### Line  69
> **Code:** `assert body["version"] == "11"`
> **Type:** Enforces a condition

### Line  70
> **Code:** `assert body["stage"] == "Staging"`
> **Type:** Enforces a condition

### Line  71
> **Code:** `assert body["run_id"]`
> **Type:** Enforces a condition

### Line  72
> **Code:** ``
> **Type:** Empty line

### Line  73
> **Code:** ``
> **Type:** Empty line

### Line  74
> **Code:** `def test_model_info_503_when_no_model(client_no_model):`
> **Type:** Function definition

### Line  75
> **Code:** `response = client_no_model.get("/model-info")`
> **Type:** Assignment/comparison

### Line  76
> **Code:** ``
> **Type:** Empty line

### Line  77
> **Code:** `assert response.status_code == 503`
> **Type:** Enforces a condition

### Line  78
> **Code:** `assert response.json()["detail"] == "No model loaded"`
> **Type:** Enforces a condition

### Line  79
> **Code:** ``
> **Type:** Empty line

### Line  80
> **Code:** ``
> **Type:** Empty line

### Line  81
> **Code:** `def test_metrics_endpoint_exposed(client):`
> **Type:** Function definition

### Line  82
> **Code:** `"""Prometheus scrape target from spec section 8 must be reachable."""`
> **Type:** Code statement

### Line  83
> **Code:** `response = client.get("/metrics")`
> **Type:** Assignment/comparison

### Line  84
> **Code:** ``
> **Type:** Empty line

### Line  85
> **Code:** `assert response.status_code == 200`
> **Type:** Enforces a condition

### Line  86
> **Code:** `assert "http_request" in response.text`
> **Type:** Enforces a condition

## Summary
- **Total lines:** 86
- **Code lines:** 55
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 28

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: test_health.py*
---

# mlops-platform-spec-detailed: conftest.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/tests/conftest.py`
- **Total lines:** 130
- **File size:** 3577 bytes

## Line Type Summary
- **Code:** 94
- **Comment:** 0
- **Empty:** 33
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Shared pytest fixtures for the predictive maintenance API test suit...`
> **Type:** Logical operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line   7
> **Code:** ``
> **Type:** Empty line

### Line   8
> **Code:** `import sys`
> **Type:** Imports a module

### Line   9
> **Code:** `from pathlib import Path`
> **Type:** Imports specific names from a module

### Line  10
> **Code:** `from typing import Any, Dict`
> **Type:** Imports specific names from a module

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `import numpy as np`
> **Type:** Imports a module

### Line  13
> **Code:** `import pytest`
> **Type:** Imports a module

### Line  14
> **Code:** ``
> **Type:** Empty line

### Line  15
> **Code:** `API_DIR = Path(__file__).resolve().parents[1]`
> **Type:** Assignment/comparison

### Line  16
> **Code:** `if str(API_DIR) not in sys.path:`
> **Type:** Conditional statement

### Line  17
> **Code:** `sys.path.insert(0, str(API_DIR))`
> **Type:** Function call

### Line  18
> **Code:** ``
> **Type:** Empty line

### Line  19
> **Code:** ``
> **Type:** Empty line

### Line  20
> **Code:** `class FakeSession:`
> **Type:** Class definition

### Line  21
> **Code:** `def __init__(self) -> None:`
> **Type:** Function definition

### Line  22
> **Code:** `self.added: list[Any] = []`
> **Type:** Assignment/comparison

### Line  23
> **Code:** `self.committed = False`
> **Type:** Assignment/comparison

### Line  24
> **Code:** `self.rolled_back = False`
> **Type:** Assignment/comparison

### Line  25
> **Code:** ``
> **Type:** Empty line

### Line  26
> **Code:** `def add(self, obj: Any) -> None:`
> **Type:** Function definition

### Line  27
> **Code:** `self.added.append(obj)`
> **Type:** Function call

### Line  28
> **Code:** ``
> **Type:** Empty line

### Line  29
> **Code:** `def commit(self) -> None:`
> **Type:** Function definition

### Line  30
> **Code:** `self.committed = True`
> **Type:** Assignment/comparison

### Line  31
> **Code:** ``
> **Type:** Empty line

### Line  32
> **Code:** `def rollback(self) -> None:`
> **Type:** Function definition

### Line  33
> **Code:** `self.rolled_back = True`
> **Type:** Assignment/comparison

### Line  34
> **Code:** ``
> **Type:** Empty line

### Line  35
> **Code:** `def close(self) -> None:`
> **Type:** Function definition

### Line  36
> **Code:** `pass`
> **Type:** Code statement

### Line  37
> **Code:** ``
> **Type:** Empty line

### Line  38
> **Code:** ``
> **Type:** Empty line

### Line  39
> **Code:** `class FakeModel:`
> **Type:** Class definition

### Line  40
> **Code:** `"""Stub model returning a fixed failure probability via predict_proba....`
> **Type:** Code statement

### Line  41
> **Code:** ``
> **Type:** Empty line

### Line  42
> **Code:** `def __init__(self, failure_prob: float = 0.75) -> None:`
> **Type:** Function definition

### Line  43
> **Code:** `self.failure_prob = failure_prob`
> **Type:** Assignment/comparison

### Line  44
> **Code:** `self.last_input: Any = None`
> **Type:** Assignment/comparison

### Line  45
> **Code:** ``
> **Type:** Empty line

### Line  46
> **Code:** `def predict_proba(self, df):`
> **Type:** Function definition

### Line  47
> **Code:** `import pandas as pd`
> **Type:** Imports a module

### Line  48
> **Code:** `self.last_input = df`
> **Type:** Assignment/comparison

### Line  49
> **Code:** `probs = np.array([[1 - self.failure_prob, self.failure_prob]] * len(df...`
> **Type:** Assignment/comparison

### Line  50
> **Code:** `return probs`
> **Type:** Returns a value from a function

### Line  51
> **Code:** ``
> **Type:** Empty line

### Line  52
> **Code:** `def predict(self, df):`
> **Type:** Function definition

### Line  53
> **Code:** `return (self.predict_proba(df)[:, 1] >= 0.5).astype(int)`
> **Type:** Returns a value from a function

### Line  54
> **Code:** ``
> **Type:** Empty line

### Line  55
> **Code:** ``
> **Type:** Empty line

### Line  56
> **Code:** `LOADED_META: Dict[str, Any] = {`
> **Type:** Assignment/comparison

### Line  57
> **Code:** `"loaded": True,`
> **Type:** Code statement

### Line  58
> **Code:** `"name": "maintenance-model",`
> **Type:** Arithmetic operation

### Line  59
> **Code:** `"version": "11",`
> **Type:** Code statement

### Line  60
> **Code:** `"stage": "Staging",`
> **Type:** Code statement

### Line  61
> **Code:** `"run_id": "abcdef1234567890abcdef1234567890",`
> **Type:** Code statement

### Line  62
> **Code:** `}`
> **Type:** Code statement

### Line  63
> **Code:** ``
> **Type:** Empty line

### Line  64
> **Code:** ``
> **Type:** Empty line

### Line  65
> **Code:** `@pytest.fixture`
> **Type:** Code statement

### Line  66
> **Code:** `def fake_session() -> FakeSession:`
> **Type:** Function definition

### Line  67
> **Code:** `return FakeSession()`
> **Type:** Returns a value from a function

### Line  68
> **Code:** ``
> **Type:** Empty line

### Line  69
> **Code:** ``
> **Type:** Empty line

### Line  70
> **Code:** `@pytest.fixture`
> **Type:** Code statement

### Line  71
> **Code:** `def fake_model() -> FakeModel:`
> **Type:** Function definition

### Line  72
> **Code:** `return FakeModel()`
> **Type:** Returns a value from a function

### Line  73
> **Code:** ``
> **Type:** Empty line

### Line  74
> **Code:** ``
> **Type:** Empty line

### Line  75
> **Code:** `@pytest.fixture`
> **Type:** Code statement

### Line  76
> **Code:** `def app_module(monkeypatch):`
> **Type:** Function definition

### Line  77
> **Code:** `import main as main_module`
> **Type:** Imports a module

### Line  78
> **Code:** `monkeypatch.setattr(main_module, "init_db", lambda: None)`
> **Type:** Function call

### Line  79
> **Code:** `monkeypatch.setattr(main_module, "load_model", lambda: None)`
> **Type:** Function call

### Line  80
> **Code:** `return main_module`
> **Type:** Returns a value from a function

### Line  81
> **Code:** ``
> **Type:** Empty line

### Line  82
> **Code:** ``
> **Type:** Empty line

### Line  83
> **Code:** `@pytest.fixture`
> **Type:** Code statement

### Line  84
> **Code:** `def client(app_module, fake_model, fake_session, monkeypatch):`
> **Type:** Function definition

### Line  85
> **Code:** `from fastapi.testclient import TestClient`
> **Type:** Imports specific names from a module

### Line  86
> **Code:** `from app import model_loader`
> **Type:** Imports specific names from a module

### Line  87
> **Code:** `from app.routers import health as health_router`
> **Type:** Imports specific names from a module

### Line  88
> **Code:** `from app.routers import predict as predict_router`
> **Type:** Imports specific names from a module

### Line  89
> **Code:** ``
> **Type:** Empty line

### Line  90
> **Code:** `monkeypatch.setattr(model_loader, "_model", fake_model)`
> **Type:** Function call

### Line  91
> **Code:** `monkeypatch.setattr(model_loader, "_model_meta", dict(LOADED_META))`
> **Type:** Function call

### Line  92
> **Code:** `monkeypatch.setattr(health_router, "check_db", lambda: True)`
> **Type:** Function call

### Line  93
> **Code:** ``
> **Type:** Empty line

### Line  94
> **Code:** `app_module.app.dependency_overrides[predict_router.get_db] = lambda: f...`
> **Type:** Assignment/comparison

### Line  95
> **Code:** `with TestClient(app_module.app) as test_client:`
> **Type:** Context manager

### Line  96
> **Code:** `yield test_client`
> **Type:** Code statement

### Line  97
> **Code:** `app_module.app.dependency_overrides.clear()`
> **Type:** Function call

### Line  98
> **Code:** ``
> **Type:** Empty line

### Line  99
> **Code:** ``
> **Type:** Empty line

### Line 100
> **Code:** `@pytest.fixture`
> **Type:** Code statement

### Line 101
> **Code:** `def client_no_model(app_module, monkeypatch):`
> **Type:** Function definition

### Line 102
> **Code:** `from fastapi.testclient import TestClient`
> **Type:** Imports specific names from a module

### Line 103
> **Code:** `from app import model_loader`
> **Type:** Imports specific names from a module

### Line 104
> **Code:** `from app.routers import health as health_router`
> **Type:** Imports specific names from a module

### Line 105
> **Code:** ``
> **Type:** Empty line

### Line 106
> **Code:** `monkeypatch.setattr(model_loader, "_model", None)`
> **Type:** Function call

### Line 107
> **Code:** `monkeypatch.setattr(`
> **Type:** Code statement

### Line 108
> **Code:** `model_loader,`
> **Type:** Code statement

### Line 109
> **Code:** `"_model_meta",`
> **Type:** Code statement

### Line 110
> **Code:** `{"loaded": False, "name": "maintenance-model", "version": None, "stage...`
> **Type:** Arithmetic operation

### Line 111
> **Code:** `)`
> **Type:** Code statement

### Line 112
> **Code:** `monkeypatch.setattr(health_router, "check_db", lambda: True)`
> **Type:** Function call

### Line 113
> **Code:** ``
> **Type:** Empty line

### Line 114
> **Code:** `with TestClient(app_module.app) as test_client:`
> **Type:** Context manager

### Line 115
> **Code:** `yield test_client`
> **Type:** Code statement

### Line 116
> **Code:** `app_module.app.dependency_overrides.clear()`
> **Type:** Function call

### Line 117
> **Code:** ``
> **Type:** Empty line

### Line 118
> **Code:** ``
> **Type:** Empty line

### Line 119
> **Code:** `@pytest.fixture`
> **Type:** Code statement

### Line 120
> **Code:** `def sample_payload() -> Dict[str, Any]:`
> **Type:** Function definition

### Line 121
> **Code:** `return {`
> **Type:** Returns a value from a function

### Line 122
> **Code:** `"equipment_type": "pump",`
> **Type:** Code statement

### Line 123
> **Code:** `"age_months": 60,`
> **Type:** Code statement

### Line 124
> **Code:** `"operating_hours": 20000.0,`
> **Type:** Code statement

### Line 125
> **Code:** `"maintenance_history": 5,`
> **Type:** Logical operation

### Line 126
> **Code:** `"sensor_temp": 70.0,`
> **Type:** Logical operation

### Line 127
> **Code:** `"sensor_vibration": 1.0,`
> **Type:** Logical operation

### Line 128
> **Code:** `"sensor_pressure": 35.0,`
> **Type:** Logical operation

### Line 129
> **Code:** `"sensor_humidity": 50.0,`
> **Type:** Logical operation

### Line 130
> **Code:** `}`
> **Type:** Code statement

## Summary
- **Total lines:** 130
- **Code lines:** 94
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 33

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: conftest.py*
---

# mlops-platform-spec-detailed: test_monitoring.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/tests/test_monitoring.py`
- **Total lines:** 91
- **File size:** 3502 bytes

## Line Type Summary
- **Code:** 72
- **Comment:** 1
- **Empty:** 15
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: high - Add alert rule for ingestion stalls`
> **Type:** TODO: high - Add alert rule for ingestion stalls

### Line   2
> **Code:** `# TODO: medium - Implement dashboard for drift detection`
> **Type:** TODO: medium - Implement dashboard for drift detection

### Line   3
> **Code:** `# TODO: low - Add prediction distribution monitoring`
> **Type:** TODO: low - Add prediction distribution monitoring

### Line   4
> **Code:** `"""Tests for the drift detector + retraining trigger (ml/monitoring/)....`
> **Type:** Arithmetic operation

### Line   5
> **Code:** `import json`
> **Type:** Imports a module

### Line   6
> **Code:** `import os`
> **Type:** Imports a module

### Line   7
> **Code:** `import sys`
> **Type:** Imports a module

### Line   8
> **Code:** `from pathlib import Path`
> **Type:** Imports specific names from a module

### Line   9
> **Code:** ``
> **Type:** Empty line

### Line  10
> **Code:** `import numpy as np`
> **Type:** Imports a module

### Line  11
> **Code:** `import pandas as pd`
> **Type:** Imports a module

### Line  12
> **Code:** `import pytest`
> **Type:** Imports a module

### Line  13
> **Code:** ``
> **Type:** Empty line

### Line  14
> **Code:** `# allow importing ml.monitoring and ml/training helpers`
> **Type:** Comment: allow importing ml.monitoring and ml/training helpers

### Line  15
> **Code:** `REPO_ROOT = Path(__file__).resolve().parents[2]`
> **Type:** Assignment/comparison

### Line  16
> **Code:** `sys.path.insert(0, str(REPO_ROOT / "ml"))`
> **Type:** Arithmetic operation

### Line  17
> **Code:** `sys.path.insert(0, str(REPO_ROOT / "ml" / "training"))`
> **Type:** Arithmetic operation

### Line  18
> **Code:** ``
> **Type:** Empty line

### Line  19
> **Code:** `from monitoring import drift_detector, retraining_trigger`
> **Type:** Imports specific names from a module

### Line  20
> **Code:** ``
> **Type:** Empty line

### Line  21
> **Code:** `NUMERIC = ["age_months", "operating_hours", "maintenance_history",`
> **Type:** Assignment/comparison

### Line  22
> **Code:** `"sensor_temp", "sensor_vibration", "sensor_pressure", "sensor_humidity...`
> **Type:** Logical operation

### Line  23
> **Code:** ``
> **Type:** Empty line

### Line  24
> **Code:** ``
> **Type:** Empty line

### Line  25
> **Code:** `def _make_maintenance(tmp_path, n=300, seed=0):`
> **Type:** Function definition

### Line  26
> **Code:** `rng = np.random.default_rng(seed)`
> **Type:** Assignment/comparison

### Line  27
> **Code:** `df = pd.DataFrame({`
> **Type:** Assignment/comparison

### Line  28
> **Code:** `"machine_id": range(n),`
> **Type:** Code statement

### Line  29
> **Code:** `"equipment_type": rng.choice(["pump", "motor", "compressor", "turbine"...`
> **Type:** Logical operation

### Line  30
> **Code:** `"age_months": rng.integers(1, 300, n),`
> **Type:** Code statement

### Line  31
> **Code:** `"operating_hours": rng.uniform(0, 200000, n),`
> **Type:** Logical operation

### Line  32
> **Code:** `"maintenance_history": rng.integers(0, 100, n),`
> **Type:** Logical operation

### Line  33
> **Code:** `"sensor_temp": rng.uniform(0, 200, n),`
> **Type:** Logical operation

### Line  34
> **Code:** `"sensor_vibration": rng.uniform(0, 15, n),`
> **Type:** Logical operation

### Line  35
> **Code:** `"sensor_pressure": rng.uniform(0, 100, n),`
> **Type:** Logical operation

### Line  36
> **Code:** `"sensor_humidity": rng.uniform(0, 100, n),`
> **Type:** Logical operation

### Line  37
> **Code:** `"failure_next_30_days": rng.binomial(1, 0.3, n),`
> **Type:** Code statement

### Line  38
> **Code:** `})`
> **Type:** Code statement

### Line  39
> **Code:** `path = tmp_path / "maintenance.csv"`
> **Type:** Assignment/comparison

### Line  40
> **Code:** `df.to_csv(path, index=False)`
> **Type:** Assignment/comparison

### Line  41
> **Code:** `return path`
> **Type:** Returns a value from a function

### Line  42
> **Code:** ``
> **Type:** Empty line

### Line  43
> **Code:** ``
> **Type:** Empty line

### Line  44
> **Code:** `def test_no_drift_when_identical(tmp_path):`
> **Type:** Function definition

### Line  45
> **Code:** `ref = _make_maintenance(tmp_path, seed=1)`
> **Type:** Assignment/comparison

### Line  46
> **Code:** `det = drift_detector.detect_drift(ref, ref)`
> **Type:** Assignment/comparison

### Line  47
> **Code:** `assert det["drift_score"] == 0.0`
> **Type:** Enforces a condition

### Line  48
> **Code:** `assert det["drift_detected"] is False`
> **Type:** Enforces a condition

### Line  49
> **Code:** ``
> **Type:** Empty line

### Line  50
> **Code:** ``
> **Type:** Empty line

### Line  51
> **Code:** `def test_drift_detected_on_shift(tmp_path):`
> **Type:** Function definition

### Line  52
> **Code:** `ref = _make_maintenance(tmp_path, seed=2)`
> **Type:** Assignment/comparison

### Line  53
> **Code:** `cur = pd.read_csv(_make_maintenance(tmp_path, seed=3))`
> **Type:** Assignment/comparison

### Line  54
> **Code:** `rng = np.random.default_rng(9)`
> **Type:** Assignment/comparison

### Line  55
> **Code:** `cur["sensor_vibration"] = cur["sensor_vibration"] * rng.normal(2.0, 0....`
> **Type:** Assignment/comparison

### Line  56
> **Code:** `cur_path = tmp_path / "maintenance_shifted.csv"`
> **Type:** Assignment/comparison

### Line  57
> **Code:** `cur.to_csv(cur_path, index=False)`
> **Type:** Assignment/comparison

### Line  58
> **Code:** `det = drift_detector.detect_drift(ref, cur_path)`
> **Type:** Assignment/comparison

### Line  59
> **Code:** `assert det["drift_score"] > 0.0`
> **Type:** Enforces a condition

### Line  60
> **Code:** `assert "sensor_vibration" in det["drifted_features"]`
> **Type:** Enforces a condition

### Line  61
> **Code:** ``
> **Type:** Empty line

### Line  62
> **Code:** ``
> **Type:** Empty line

### Line  63
> **Code:** `def test_trigger_fires_when_drifted(tmp_path):`
> **Type:** Function definition

### Line  64
> **Code:** `ref = _make_maintenance(tmp_path, seed=4)`
> **Type:** Assignment/comparison

### Line  65
> **Code:** `cur = pd.read_csv(ref)`
> **Type:** Assignment/comparison

### Line  66
> **Code:** `rng = np.random.default_rng(5)`
> **Type:** Assignment/comparison

### Line  67
> **Code:** `for col, mult, sd in [("sensor_vibration", 2.5, 0.5),`
> **Type:** For loop

### Line  68
> **Code:** `("sensor_temp", 1.6, 0.4),`
> **Type:** Logical operation

### Line  69
> **Code:** `("operating_hours", 1.8, 0.5)]:`
> **Type:** Code statement

### Line  70
> **Code:** `cur[col] = cur[col] * rng.normal(mult, sd, size=len(cur))`
> **Type:** Assignment/comparison

### Line  71
> **Code:** `cur_path = tmp_path / "maintenance_shifted2.csv"`
> **Type:** Assignment/comparison

### Line  72
> **Code:** `cur.to_csv(cur_path, index=False)`
> **Type:** Assignment/comparison

### Line  73
> **Code:** `det = drift_detector.detect_drift(ref, cur_path)`
> **Type:** Assignment/comparison

### Line  74
> **Code:** `assert det["drift_detected"] is True`
> **Type:** Enforces a condition

### Line  75
> **Code:** ``
> **Type:** Empty line

### Line  76
> **Code:** `report_path = drift_detector.REPORT_PATH`
> **Type:** Assignment/comparison

### Line  77
> **Code:** `report_path.parent.mkdir(parents=True, exist_ok=True)`
> **Type:** Assignment/comparison

### Line  78
> **Code:** `report_path.write_text(json.dumps(det))`
> **Type:** Logical operation

### Line  79
> **Code:** `result = retraining_trigger.trigger_retraining(dry_run=True)`
> **Type:** Assignment/comparison

### Line  80
> **Code:** `assert result["triggered"] is True`
> **Type:** Enforces a condition

### Line  81
> **Code:** `assert result["dry_run"] is True`
> **Type:** Enforces a condition

### Line  82
> **Code:** ``
> **Type:** Empty line

### Line  83
> **Code:** ``
> **Type:** Empty line

### Line  84
> **Code:** `def test_trigger_does_not_fire_without_drift(tmp_path):`
> **Type:** Function definition

### Line  85
> **Code:** `ref = _make_maintenance(tmp_path, seed=6)`
> **Type:** Assignment/comparison

### Line  86
> **Code:** `det = drift_detector.detect_drift(ref, ref)`
> **Type:** Assignment/comparison

### Line  87
> **Code:** `report_path = drift_detector.REPORT_PATH`
> **Type:** Assignment/comparison

### Line  88
> **Code:** `report_path.parent.mkdir(parents=True, exist_ok=True)`
> **Type:** Assignment/comparison

### Line  89
> **Code:** `report_path.write_text(json.dumps(det))`
> **Type:** Logical operation

### Line  90
> **Code:** `result = retraining_trigger.trigger_retraining(dry_run=True)`
> **Type:** Assignment/comparison

### Line  91
> **Code:** `assert result["triggered"] is False`
> **Type:** Enforces a condition

## Summary
- **Total lines:** 91
- **Code lines:** 72
- **Comments:** 1
- **TODO items:** 3
- **Empty lines:** 15

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: test_monitoring.py*
---

# mlops-platform-spec-detailed: model_loader.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/app/model_loader.py`
- **Total lines:** 98
- **File size:** 2474 bytes

## Line Type Summary
- **Code:** 71
- **Comment:** 0
- **Empty:** 24
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Model loader - loads the model from MLflow Model Registry on startu...`
> **Type:** Arithmetic operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line   7
> **Code:** ``
> **Type:** Empty line

### Line   8
> **Code:** `import logging`
> **Type:** Imports a module

### Line   9
> **Code:** `import os`
> **Type:** Imports a module

### Line  10
> **Code:** `import threading`
> **Type:** Imports a module

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `import mlflow.pyfunc`
> **Type:** Imports a module

### Line  13
> **Code:** ``
> **Type:** Empty line

### Line  14
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  15
> **Code:** ``
> **Type:** Empty line

### Line  16
> **Code:** `_model = None`
> **Type:** Assignment/comparison

### Line  17
> **Code:** `_model_lock = threading.Lock()`
> **Type:** Assignment/comparison

### Line  18
> **Code:** `_model_meta = {`
> **Type:** Assignment/comparison

### Line  19
> **Code:** `"loaded": False,`
> **Type:** Code statement

### Line  20
> **Code:** `"name": None,`
> **Type:** Code statement

### Line  21
> **Code:** `"version": None,`
> **Type:** Code statement

### Line  22
> **Code:** `"stage": None,`
> **Type:** Code statement

### Line  23
> **Code:** `"run_id": None,`
> **Type:** Code statement

### Line  24
> **Code:** `}`
> **Type:** Code statement

### Line  25
> **Code:** ``
> **Type:** Empty line

### Line  26
> **Code:** ``
> **Type:** Empty line

### Line  27
> **Code:** `def _tracking_uri() -> str:`
> **Type:** Function definition

### Line  28
> **Code:** `return os.getenv("MLFLOW_TRACKING_URI", "http://10.0.2.30:5000")`
> **Type:** Returns a value from a function

### Line  29
> **Code:** ``
> **Type:** Empty line

### Line  30
> **Code:** ``
> **Type:** Empty line

### Line  31
> **Code:** `def _model_name() -> str:`
> **Type:** Function definition

### Line  32
> **Code:** `return os.getenv("MODEL_NAME", "maintenance-model")`
> **Type:** Returns a value from a function

### Line  33
> **Code:** ``
> **Type:** Empty line

### Line  34
> **Code:** ``
> **Type:** Empty line

### Line  35
> **Code:** `def _model_stage() -> str:`
> **Type:** Function definition

### Line  36
> **Code:** `return os.getenv("MODEL_STAGE", "Staging")`
> **Type:** Returns a value from a function

### Line  37
> **Code:** ``
> **Type:** Empty line

### Line  38
> **Code:** ``
> **Type:** Empty line

### Line  39
> **Code:** `def load_model() -> None:`
> **Type:** Function definition

### Line  40
> **Code:** `"""Load the model from MLflow Model Registry by name + stage."""`
> **Type:** Arithmetic operation

### Line  41
> **Code:** `global _model, _model_meta`
> **Type:** Code statement

### Line  42
> **Code:** ``
> **Type:** Empty line

### Line  43
> **Code:** `tracking = _tracking_uri()`
> **Type:** Assignment/comparison

### Line  44
> **Code:** `name = _model_name()`
> **Type:** Assignment/comparison

### Line  45
> **Code:** `stage = _model_stage()`
> **Type:** Assignment/comparison

### Line  46
> **Code:** ``
> **Type:** Empty line

### Line  47
> **Code:** `logger.info("Loading model from MLflow: %s/%s (tracking: %s)", name, s...`
> **Type:** Arithmetic operation

### Line  48
> **Code:** ``
> **Type:** Empty line

### Line  49
> **Code:** `try:`
> **Type:** Code statement

### Line  50
> **Code:** `mlflow.set_tracking_uri(tracking)`
> **Type:** Function call

### Line  51
> **Code:** `model = mlflow.pyfunc.load_model(f"models:/{name}/{stage}")`
> **Type:** Assignment/comparison

### Line  52
> **Code:** ``
> **Type:** Empty line

### Line  53
> **Code:** `_model = model`
> **Type:** Assignment/comparison

### Line  54
> **Code:** `client = mlflow.tracking.MlflowClient()`
> **Type:** Assignment/comparison

### Line  55
> **Code:** `mv = client.get_latest_versions(name, stages=[stage])`
> **Type:** Assignment/comparison

### Line  56
> **Code:** `version = mv[0].version if mv else "unknown"`
> **Type:** Assignment/comparison

### Line  57
> **Code:** `run_id = mv[0].run_id if mv else "unknown"`
> **Type:** Assignment/comparison

### Line  58
> **Code:** ``
> **Type:** Empty line

### Line  59
> **Code:** `_model_meta = {`
> **Type:** Assignment/comparison

### Line  60
> **Code:** `"loaded": True,`
> **Type:** Code statement

### Line  61
> **Code:** `"name": name,`
> **Type:** Code statement

### Line  62
> **Code:** `"version": version,`
> **Type:** Code statement

### Line  63
> **Code:** `"stage": stage,`
> **Type:** Code statement

### Line  64
> **Code:** `"run_id": run_id,`
> **Type:** Code statement

### Line  65
> **Code:** `}`
> **Type:** Code statement

### Line  66
> **Code:** `logger.info(`
> **Type:** Code statement

### Line  67
> **Code:** `"Model loaded successfully: name=%s version=%s stage=%s run_id=%s",`
> **Type:** Assignment/comparison

### Line  68
> **Code:** `name,`
> **Type:** Code statement

### Line  69
> **Code:** `version,`
> **Type:** Code statement

### Line  70
> **Code:** `stage,`
> **Type:** Code statement

### Line  71
> **Code:** `run_id,`
> **Type:** Code statement

### Line  72
> **Code:** `)`
> **Type:** Code statement

### Line  73
> **Code:** `except Exception as exc:`
> **Type:** Code statement

### Line  74
> **Code:** `logger.exception("Failed to load model from MLflow: %s", exc)`
> **Type:** Arithmetic operation

### Line  75
> **Code:** `_model = None`
> **Type:** Assignment/comparison

### Line  76
> **Code:** `_model_meta = {`
> **Type:** Assignment/comparison

### Line  77
> **Code:** `"loaded": False,`
> **Type:** Code statement

### Line  78
> **Code:** `"name": name,`
> **Type:** Code statement

### Line  79
> **Code:** `"version": None,`
> **Type:** Code statement

### Line  80
> **Code:** `"stage": stage,`
> **Type:** Code statement

### Line  81
> **Code:** `"run_id": None,`
> **Type:** Code statement

### Line  82
> **Code:** `}`
> **Type:** Code statement

### Line  83
> **Code:** ``
> **Type:** Empty line

### Line  84
> **Code:** ``
> **Type:** Empty line

### Line  85
> **Code:** `def get_model():`
> **Type:** Function definition

### Line  86
> **Code:** `"""Return the loaded model (or None if not loaded)."""`
> **Type:** Logical operation

### Line  87
> **Code:** `return _model`
> **Type:** Returns a value from a function

### Line  88
> **Code:** ``
> **Type:** Empty line

### Line  89
> **Code:** ``
> **Type:** Empty line

### Line  90
> **Code:** `def model_metadata() -> dict:`
> **Type:** Function definition

### Line  91
> **Code:** `"""Return metadata about the currently loaded model."""`
> **Type:** Code statement

### Line  92
> **Code:** `return _model_meta.copy()`
> **Type:** Returns a value from a function

### Line  93
> **Code:** ``
> **Type:** Empty line

### Line  94
> **Code:** ``
> **Type:** Empty line

### Line  95
> **Code:** `def reload_model() -> None:`
> **Type:** Function definition

### Line  96
> **Code:** `"""Admin-triggered reload (e.g., after a new model is promoted to Prod...`
> **Type:** Arithmetic operation

### Line  97
> **Code:** `with _model_lock:`
> **Type:** Context manager

### Line  98
> **Code:** `load_model()`
> **Type:** Function call

## Summary
- **Total lines:** 98
- **Code lines:** 71
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 24

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: model_loader.py*
---

# mlops-platform-spec-detailed: __init__.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/app/__init__.py`
- **Total lines:** 4
- **File size:** 226 bytes

## Line Type Summary
- **Code:** 1
- **Comment:** 0
- **Empty:** 0
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""app package: FastAPI application for the predictive maintenance pre...`
> **Type:** Logical operation

## Summary
- **Total lines:** 4
- **Code lines:** 1
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 0

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: __init__.py*
---

# mlops-platform-spec-detailed: metrics.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/app/metrics.py`
- **Total lines:** 32
- **File size:** 1106 bytes

## Line Type Summary
- **Code:** 22
- **Comment:** 2
- **Empty:** 5
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Prometheus metrics configuration for FastAPI.`
> **Type:** Logical operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `Uses prometheus-fastapi-instrumentator to expose:`
> **Type:** Arithmetic operation

### Line   7
> **Code:** `- http_requests_total (counter with status, method, path)`
> **Type:** Arithmetic operation

### Line   8
> **Code:** `- http_request_duration_seconds (histogram with method, path, le)`
> **Type:** Arithmetic operation

### Line   9
> **Code:** `- fastapi_model_loaded (gauge: 1 when model loaded, 0 otherwise)`
> **Type:** Arithmetic operation

### Line  10
> **Code:** `"""`
> **Type:** Code statement

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  13
> **Code:** ``
> **Type:** Empty line

### Line  14
> **Code:** `from prometheus_client import Gauge`
> **Type:** Imports specific names from a module

### Line  15
> **Code:** `from prometheus_fastapi_instrumentator import Instrumentator`
> **Type:** Imports specific names from a module

### Line  16
> **Code:** ``
> **Type:** Empty line

### Line  17
> **Code:** `# Custom gauge: 1 if model is loaded, 0 otherwise.`
> **Type:** Comment: Custom gauge: 1 if model is loaded, 0 otherwise.

### Line  18
> **Code:** `model_loaded_gauge = Gauge(`
> **Type:** Assignment/comparison

### Line  19
> **Code:** `"fastapi_model_loaded",`
> **Type:** Code statement

### Line  20
> **Code:** `"Whether a model is currently loaded (1=yes, 0=no)",`
> **Type:** Assignment/comparison

### Line  21
> **Code:** `)`
> **Type:** Code statement

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `# FastAPI instrumentator with sensible defaults for ML serving.`
> **Type:** Comment: FastAPI instrumentator with sensible defaults for ML serving.

### Line  24
> **Code:** `instrumentator = Instrumentator(`
> **Type:** Assignment/comparison

### Line  25
> **Code:** `should_group_status_codes=False,`
> **Type:** Assignment/comparison

### Line  26
> **Code:** `should_ignore_untemplated=True,`
> **Type:** Assignment/comparison

### Line  27
> **Code:** `should_respect_env_var=True,`
> **Type:** Assignment/comparison

### Line  28
> **Code:** `should_instrument_requests_inprogress=True,`
> **Type:** Assignment/comparison

### Line  29
> **Code:** `excluded_handlers=["/metrics", "/health"],`
> **Type:** Assignment/comparison

### Line  30
> **Code:** `inprogress_name="http_requests_inprogress",`
> **Type:** Assignment/comparison

### Line  31
> **Code:** `inprogress_labels=True,`
> **Type:** Assignment/comparison

### Line  32
> **Code:** `)`
> **Type:** Code statement

## Summary
- **Total lines:** 32
- **Code lines:** 22
- **Comments:** 2
- **TODO items:** 3
- **Empty lines:** 5

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: metrics.py*
---

# mlops-platform-spec-detailed: db.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/app/db.py`
- **Total lines:** 82
- **File size:** 2288 bytes

## Line Type Summary
- **Code:** 59
- **Comment:** 0
- **Empty:** 20
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Database layer for prediction logging (SQLite-compatible)."""`
> **Type:** Arithmetic operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line   7
> **Code:** ``
> **Type:** Empty line

### Line   8
> **Code:** `import logging`
> **Type:** Imports a module

### Line   9
> **Code:** `import os`
> **Type:** Imports a module

### Line  10
> **Code:** `from datetime import datetime`
> **Type:** Imports specific names from a module

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `from sqlalchemy import (`
> **Type:** Imports specific names from a module

### Line  13
> **Code:** `Column,`
> **Type:** Code statement

### Line  14
> **Code:** `DateTime,`
> **Type:** Code statement

### Line  15
> **Code:** `Float,`
> **Type:** Code statement

### Line  16
> **Code:** `Integer,`
> **Type:** Code statement

### Line  17
> **Code:** `String,`
> **Type:** Code statement

### Line  18
> **Code:** `Text,`
> **Type:** Code statement

### Line  19
> **Code:** `create_engine,`
> **Type:** Code statement

### Line  20
> **Code:** `)`
> **Type:** Code statement

### Line  21
> **Code:** `from sqlalchemy.orm import declarative_base, sessionmaker`
> **Type:** Imports specific names from a module

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  24
> **Code:** ``
> **Type:** Empty line

### Line  25
> **Code:** `Base = declarative_base()`
> **Type:** Assignment/comparison

### Line  26
> **Code:** ``
> **Type:** Empty line

### Line  27
> **Code:** ``
> **Type:** Empty line

### Line  28
> **Code:** `class PredictionLog(Base):`
> **Type:** Class definition

### Line  29
> **Code:** `__tablename__ = "predictions"`
> **Type:** Assignment/comparison

### Line  30
> **Code:** ``
> **Type:** Empty line

### Line  31
> **Code:** `id = Column(Integer, primary_key=True, autoincrement=True)`
> **Type:** Assignment/comparison

### Line  32
> **Code:** `input_payload = Column(Text, nullable=False)`
> **Type:** Assignment/comparison

### Line  33
> **Code:** `prediction = Column(String(50), nullable=False)`
> **Type:** Assignment/comparison

### Line  34
> **Code:** `probability = Column(Float, nullable=True)`
> **Type:** Assignment/comparison

### Line  35
> **Code:** `model_name = Column(String(100), nullable=True)`
> **Type:** Assignment/comparison

### Line  36
> **Code:** `model_version = Column(String(20), nullable=True)`
> **Type:** Assignment/comparison

### Line  37
> **Code:** `model_stage = Column(String(20), nullable=True)`
> **Type:** Assignment/comparison

### Line  38
> **Code:** `latency_ms = Column(Float, nullable=True)`
> **Type:** Assignment/comparison

### Line  39
> **Code:** `created_at = Column(DateTime, default=datetime.utcnow, nullable=False)`
> **Type:** Assignment/comparison

### Line  40
> **Code:** ``
> **Type:** Empty line

### Line  41
> **Code:** ``
> **Type:** Empty line

### Line  42
> **Code:** `_engine = None`
> **Type:** Assignment/comparison

### Line  43
> **Code:** `_SessionFactory = None`
> **Type:** Assignment/comparison

### Line  44
> **Code:** ``
> **Type:** Empty line

### Line  45
> **Code:** ``
> **Type:** Empty line

### Line  46
> **Code:** `def _database_url() -> str:`
> **Type:** Function definition

### Line  47
> **Code:** `sqlite_path = os.environ.get("SQLITE_DB", os.path.join(os.path.dirname...`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `if os.getenv("DB_HOST"):`
> **Type:** Conditional statement

### Line  49
> **Code:** `user = os.getenv("DB_USER", "mlops_app")`
> **Type:** Assignment/comparison

### Line  50
> **Code:** `password = os.getenv("DB_PASSWORD", "changeme_app")`
> **Type:** Assignment/comparison

### Line  51
> **Code:** `host = os.getenv("DB_HOST", "10.0.2.40")`
> **Type:** Assignment/comparison

### Line  52
> **Code:** `port = os.getenv("DB_PORT", "5432")`
> **Type:** Assignment/comparison

### Line  53
> **Code:** `name = os.getenv("DB_NAME", "mlops")`
> **Type:** Assignment/comparison

### Line  54
> **Code:** `return f"postgresql://{user}:{password}@{host}:{port}/{name}"`
> **Type:** Returns a value from a function

### Line  55
> **Code:** `return f"sqlite:///{sqlite_path}"`
> **Type:** Returns a value from a function

### Line  56
> **Code:** ``
> **Type:** Empty line

### Line  57
> **Code:** ``
> **Type:** Empty line

### Line  58
> **Code:** `def get_engine():`
> **Type:** Function definition

### Line  59
> **Code:** `global _engine`
> **Type:** Code statement

### Line  60
> **Code:** `if _engine is None:`
> **Type:** Conditional statement

### Line  61
> **Code:** `_engine = create_engine(_database_url(), pool_pre_ping=True)`
> **Type:** Assignment/comparison

### Line  62
> **Code:** `return _engine`
> **Type:** Returns a value from a function

### Line  63
> **Code:** ``
> **Type:** Empty line

### Line  64
> **Code:** ``
> **Type:** Empty line

### Line  65
> **Code:** `def get_session_factory():`
> **Type:** Function definition

### Line  66
> **Code:** `global _SessionFactory`
> **Type:** Logical operation

### Line  67
> **Code:** `if _SessionFactory is None:`
> **Type:** Conditional statement

### Line  68
> **Code:** `_SessionFactory = sessionmaker(bind=get_engine())`
> **Type:** Assignment/comparison

### Line  69
> **Code:** `return _SessionFactory`
> **Type:** Returns a value from a function

### Line  70
> **Code:** ``
> **Type:** Empty line

### Line  71
> **Code:** ``
> **Type:** Empty line

### Line  72
> **Code:** `def SessionLocal():`
> **Type:** Function definition

### Line  73
> **Code:** `return get_session_factory()()`
> **Type:** Returns a value from a function

### Line  74
> **Code:** ``
> **Type:** Empty line

### Line  75
> **Code:** ``
> **Type:** Empty line

### Line  76
> **Code:** `def init_db() -> None:`
> **Type:** Function definition

### Line  77
> **Code:** `try:`
> **Type:** Code statement

### Line  78
> **Code:** `Base.metadata.create_all(bind=get_engine())`
> **Type:** Assignment/comparison

### Line  79
> **Code:** `logger.info("Database tables initialized")`
> **Type:** Function call

### Line  80
> **Code:** `except Exception as exc:`
> **Type:** Code statement

### Line  81
> **Code:** `logger.exception("Failed to initialize database: %s", exc)`
> **Type:** Arithmetic operation

### Line  82
> **Code:** `raise`
> **Type:** Raises an exception

## Summary
- **Total lines:** 82
- **Code lines:** 59
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 20

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: db.py*
---

# mlops-platform-spec-detailed: schemas.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/app/schemas.py`
- **Total lines:** 61
- **File size:** 2221 bytes

## Line Type Summary
- **Code:** 42
- **Comment:** 0
- **Empty:** 16
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Pydantic request/response models for the predictive maintenance API...`
> **Type:** Arithmetic operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line   7
> **Code:** ``
> **Type:** Empty line

### Line   8
> **Code:** `from pydantic import BaseModel, Field`
> **Type:** Imports specific names from a module

### Line   9
> **Code:** `from typing import Any, Dict, Literal, Optional`
> **Type:** Imports specific names from a module

### Line  10
> **Code:** ``
> **Type:** Empty line

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `class PredictRequest(BaseModel):`
> **Type:** Class definition

### Line  13
> **Code:** `"""Predictive maintenance prediction request.`
> **Type:** Code statement

### Line  14
> **Code:** ``
> **Type:** Empty line

### Line  15
> **Code:** `Equipment sensor data for failure prediction within 30 days.`
> **Type:** Logical operation

### Line  16
> **Code:** `"""`
> **Type:** Code statement

### Line  17
> **Code:** ``
> **Type:** Empty line

### Line  18
> **Code:** `equipment_type: Literal["pump", "motor", "compressor", "turbine"] = Fi...`
> **Type:** Assignment/comparison

### Line  19
> **Code:** `default="pump", description="Type of industrial equipment"`
> **Type:** Assignment/comparison

### Line  20
> **Code:** `)`
> **Type:** Code statement

### Line  21
> **Code:** `age_months: int = Field(default=60, ge=1, le=300, description="Equipme...`
> **Type:** Assignment/comparison

### Line  22
> **Code:** `operating_hours: float = Field(default=20000.0, ge=0, le=200000, descr...`
> **Type:** Assignment/comparison

### Line  23
> **Code:** `maintenance_history: int = Field(default=5, ge=0, le=100, description=...`
> **Type:** Assignment/comparison

### Line  24
> **Code:** `sensor_temp: float = Field(default=70.0, ge=0, le=200, description="Te...`
> **Type:** Assignment/comparison

### Line  25
> **Code:** `sensor_vibration: float = Field(default=1.0, ge=0, le=15, description=...`
> **Type:** Assignment/comparison

### Line  26
> **Code:** `sensor_pressure: float = Field(default=35.0, ge=0, le=100, description...`
> **Type:** Assignment/comparison

### Line  27
> **Code:** `sensor_humidity: float = Field(default=50.0, ge=0, le=100, description...`
> **Type:** Assignment/comparison

### Line  28
> **Code:** ``
> **Type:** Empty line

### Line  29
> **Code:** `class Config:`
> **Type:** Class definition

### Line  30
> **Code:** `populate_by_name = True`
> **Type:** Assignment/comparison

### Line  31
> **Code:** ``
> **Type:** Empty line

### Line  32
> **Code:** ``
> **Type:** Empty line

### Line  33
> **Code:** `class PredictResponse(BaseModel):`
> **Type:** Class definition

### Line  34
> **Code:** `"""Predictive maintenance prediction response."""`
> **Type:** Code statement

### Line  35
> **Code:** ``
> **Type:** Empty line

### Line  36
> **Code:** `prediction: Literal["failure", "no_failure"]`
> **Type:** Data structure operation

### Line  37
> **Code:** `probability: float = Field(ge=0.0, le=1.0)`
> **Type:** Assignment/comparison

### Line  38
> **Code:** `risk_level: str = Field(description="Risk tier: critical, high, medium...`
> **Type:** Assignment/comparison

### Line  39
> **Code:** `model_version: str`
> **Type:** Code statement

### Line  40
> **Code:** `model_stage: str`
> **Type:** Code statement

### Line  41
> **Code:** ``
> **Type:** Empty line

### Line  42
> **Code:** ``
> **Type:** Empty line

### Line  43
> **Code:** `class HealthResponse(BaseModel):`
> **Type:** Class definition

### Line  44
> **Code:** `"""Health check response."""`
> **Type:** Code statement

### Line  45
> **Code:** ``
> **Type:** Empty line

### Line  46
> **Code:** `status: Literal["healthy", "degraded", "unhealthy"]`
> **Type:** Data structure operation

### Line  47
> **Code:** `db_connected: bool`
> **Type:** Code statement

### Line  48
> **Code:** `model_loaded: bool`
> **Type:** Code statement

### Line  49
> **Code:** `model_name: Optional[str] = None`
> **Type:** Assignment/comparison

### Line  50
> **Code:** `model_version: Optional[str] = None`
> **Type:** Assignment/comparison

### Line  51
> **Code:** `model_stage: Optional[str] = None`
> **Type:** Assignment/comparison

### Line  52
> **Code:** ``
> **Type:** Empty line

### Line  53
> **Code:** ``
> **Type:** Empty line

### Line  54
> **Code:** `class ModelInfoResponse(BaseModel):`
> **Type:** Class definition

### Line  55
> **Code:** `"""Detailed model information."""`
> **Type:** Logical operation

### Line  56
> **Code:** ``
> **Type:** Empty line

### Line  57
> **Code:** `name: str`
> **Type:** Code statement

### Line  58
> **Code:** `version: str`
> **Type:** Code statement

### Line  59
> **Code:** `stage: str`
> **Type:** Code statement

### Line  60
> **Code:** `run_id: Optional[str] = None`
> **Type:** Assignment/comparison

### Line  61
> **Code:** `metrics: Dict[str, float] = {}`
> **Type:** Assignment/comparison

## Summary
- **Total lines:** 61
- **Code lines:** 42
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 16

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: schemas.py*
---

# mlops-platform-spec-detailed: health.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/app/routers/health.py`
- **Total lines:** 59
- **File size:** 1593 bytes

## Line Type Summary
- **Code:** 44
- **Comment:** 0
- **Empty:** 12
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Health check router."""`
> **Type:** Code statement

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line   7
> **Code:** ``
> **Type:** Empty line

### Line   8
> **Code:** `from fastapi import APIRouter, Depends, HTTPException`
> **Type:** Imports specific names from a module

### Line   9
> **Code:** `from sqlalchemy import text`
> **Type:** Imports specific names from a module

### Line  10
> **Code:** ``
> **Type:** Empty line

### Line  11
> **Code:** `from app.db import SessionLocal`
> **Type:** Imports specific names from a module

### Line  12
> **Code:** `from app.model_loader import model_metadata, get_model`
> **Type:** Imports specific names from a module

### Line  13
> **Code:** `from app.schemas import HealthResponse`
> **Type:** Imports specific names from a module

### Line  14
> **Code:** ``
> **Type:** Empty line

### Line  15
> **Code:** `router = APIRouter(tags=["health"])`
> **Type:** Assignment/comparison

### Line  16
> **Code:** ``
> **Type:** Empty line

### Line  17
> **Code:** ``
> **Type:** Empty line

### Line  18
> **Code:** `def check_db() -> bool:`
> **Type:** Function definition

### Line  19
> **Code:** `"""Check if database is reachable."""`
> **Type:** Code statement

### Line  20
> **Code:** `try:`
> **Type:** Code statement

### Line  21
> **Code:** `db = SessionLocal()`
> **Type:** Assignment/comparison

### Line  22
> **Code:** `db.execute(text("SELECT 1"))`
> **Type:** Function call

### Line  23
> **Code:** `db.close()`
> **Type:** Function call

### Line  24
> **Code:** `return True`
> **Type:** Returns a value from a function

### Line  25
> **Code:** `except Exception:`
> **Type:** Code statement

### Line  26
> **Code:** `return False`
> **Type:** Returns a value from a function

### Line  27
> **Code:** ``
> **Type:** Empty line

### Line  28
> **Code:** ``
> **Type:** Empty line

### Line  29
> **Code:** `@router.get("/health", response_model=HealthResponse)`
> **Type:** Assignment/comparison

### Line  30
> **Code:** `async def health_check():`
> **Type:** Code statement

### Line  31
> **Code:** `"""Health endpoint for Kubernetes liveness/readiness probes."""`
> **Type:** Arithmetic operation

### Line  32
> **Code:** `db_ok = check_db()`
> **Type:** Assignment/comparison

### Line  33
> **Code:** `meta = model_metadata()`
> **Type:** Assignment/comparison

### Line  34
> **Code:** `model_ok = meta.get("loaded", False)`
> **Type:** Assignment/comparison

### Line  35
> **Code:** ``
> **Type:** Empty line

### Line  36
> **Code:** `if db_ok and model_ok:`
> **Type:** Conditional statement

### Line  37
> **Code:** `status = "healthy"`
> **Type:** Assignment/comparison

### Line  38
> **Code:** `elif not db_ok and not model_ok:`
> **Type:** Else-if branch

### Line  39
> **Code:** `status = "unhealthy"`
> **Type:** Assignment/comparison

### Line  40
> **Code:** `else:`
> **Type:** Else block

### Line  41
> **Code:** `status = "degraded"`
> **Type:** Assignment/comparison

### Line  42
> **Code:** ``
> **Type:** Empty line

### Line  43
> **Code:** `return HealthResponse(`
> **Type:** Returns a value from a function

### Line  44
> **Code:** `status=status,`
> **Type:** Assignment/comparison

### Line  45
> **Code:** `db_connected=db_ok,`
> **Type:** Assignment/comparison

### Line  46
> **Code:** `model_loaded=model_ok,`
> **Type:** Assignment/comparison

### Line  47
> **Code:** `model_name=meta.get("name"),`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `model_version=str(meta.get("version")),`
> **Type:** Assignment/comparison

### Line  49
> **Code:** `model_stage=meta.get("stage"),`
> **Type:** Assignment/comparison

### Line  50
> **Code:** `)`
> **Type:** Code statement

### Line  51
> **Code:** ``
> **Type:** Empty line

### Line  52
> **Code:** ``
> **Type:** Empty line

### Line  53
> **Code:** `@router.get("/model-info")`
> **Type:** Arithmetic operation

### Line  54
> **Code:** `async def model_info():`
> **Type:** Code statement

### Line  55
> **Code:** `"""Detailed model information (useful for debugging which model is ser...`
> **Type:** Logical operation

### Line  56
> **Code:** `meta = model_metadata()`
> **Type:** Assignment/comparison

### Line  57
> **Code:** `if not meta.get("loaded"):`
> **Type:** Conditional statement

### Line  58
> **Code:** `raise HTTPException(status_code=503, detail="No model loaded")`
> **Type:** Raises an exception

### Line  59
> **Code:** `return meta`
> **Type:** Returns a value from a function

## Summary
- **Total lines:** 59
- **Code lines:** 44
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 12

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: health.py*
---

# mlops-platform-spec-detailed: predict.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/api/app/routers/predict.py`
- **Total lines:** 104
- **File size:** 2794 bytes

## Line Type Summary
- **Code:** 81
- **Comment:** 0
- **Empty:** 20
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   2
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   3
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   4
> **Code:** `"""Prediction router for predictive maintenance."""`
> **Type:** Logical operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line   7
> **Code:** ``
> **Type:** Empty line

### Line   8
> **Code:** `import logging`
> **Type:** Imports a module

### Line   9
> **Code:** `import time`
> **Type:** Imports a module

### Line  10
> **Code:** ``
> **Type:** Empty line

### Line  11
> **Code:** `from fastapi import APIRouter, Depends, HTTPException, Request`
> **Type:** Imports specific names from a module

### Line  12
> **Code:** `from sqlalchemy.orm import Session`
> **Type:** Imports specific names from a module

### Line  13
> **Code:** ``
> **Type:** Empty line

### Line  14
> **Code:** `from app.db import SessionLocal, PredictionLog`
> **Type:** Imports specific names from a module

### Line  15
> **Code:** `from app.model_loader import get_model, model_metadata`
> **Type:** Imports specific names from a module

### Line  16
> **Code:** `from app.schemas import PredictRequest, PredictResponse`
> **Type:** Imports specific names from a module

### Line  17
> **Code:** ``
> **Type:** Empty line

### Line  18
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  19
> **Code:** ``
> **Type:** Empty line

### Line  20
> **Code:** `router = APIRouter(tags=["prediction"])`
> **Type:** Assignment/comparison

### Line  21
> **Code:** ``
> **Type:** Empty line

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `def get_db() -> Session:`
> **Type:** Function definition

### Line  24
> **Code:** `db = SessionLocal()`
> **Type:** Assignment/comparison

### Line  25
> **Code:** `try:`
> **Type:** Code statement

### Line  26
> **Code:** `yield db`
> **Type:** Code statement

### Line  27
> **Code:** `finally:`
> **Type:** Code statement

### Line  28
> **Code:** `db.close()`
> **Type:** Function call

### Line  29
> **Code:** ``
> **Type:** Empty line

### Line  30
> **Code:** ``
> **Type:** Empty line

### Line  31
> **Code:** `def _risk_level(prob: float) -> str:`
> **Type:** Function definition

### Line  32
> **Code:** `if prob >= 0.7:`
> **Type:** Conditional statement

### Line  33
> **Code:** `return "critical"`
> **Type:** Returns a value from a function

### Line  34
> **Code:** `if prob >= 0.4:`
> **Type:** Conditional statement

### Line  35
> **Code:** `return "high"`
> **Type:** Returns a value from a function

### Line  36
> **Code:** `if prob >= 0.2:`
> **Type:** Conditional statement

### Line  37
> **Code:** `return "medium"`
> **Type:** Returns a value from a function

### Line  38
> **Code:** `return "low"`
> **Type:** Returns a value from a function

### Line  39
> **Code:** ``
> **Type:** Empty line

### Line  40
> **Code:** ``
> **Type:** Empty line

### Line  41
> **Code:** `@router.post("/predict", response_model=PredictResponse)`
> **Type:** Assignment/comparison

### Line  42
> **Code:** `async def predict(`
> **Type:** Code statement

### Line  43
> **Code:** `request: PredictRequest,`
> **Type:** Code statement

### Line  44
> **Code:** `http_request: Request,`
> **Type:** Code statement

### Line  45
> **Code:** `db: Session = Depends(get_db),`
> **Type:** Assignment/comparison

### Line  46
> **Code:** `):`
> **Type:** Code statement

### Line  47
> **Code:** `"""Predict equipment failure probability within 30 days."""`
> **Type:** Code statement

### Line  48
> **Code:** `start = time.perf_counter()`
> **Type:** Assignment/comparison

### Line  49
> **Code:** ``
> **Type:** Empty line

### Line  50
> **Code:** `model = get_model()`
> **Type:** Assignment/comparison

### Line  51
> **Code:** `if model is None:`
> **Type:** Conditional statement

### Line  52
> **Code:** `logger.error("Prediction requested but no model loaded")`
> **Type:** Logical operation

### Line  53
> **Code:** `raise HTTPException(status_code=503, detail="Model not loaded")`
> **Type:** Raises an exception

### Line  54
> **Code:** ``
> **Type:** Empty line

### Line  55
> **Code:** `meta = model_metadata()`
> **Type:** Assignment/comparison

### Line  56
> **Code:** `input_dict = request.model_dump()`
> **Type:** Assignment/comparison

### Line  57
> **Code:** ``
> **Type:** Empty line

### Line  58
> **Code:** `try:`
> **Type:** Code statement

### Line  59
> **Code:** `import pandas as pd`
> **Type:** Imports a module

### Line  60
> **Code:** `df = pd.DataFrame([input_dict])`
> **Type:** Assignment/comparison

### Line  61
> **Code:** ``
> **Type:** Empty line

### Line  62
> **Code:** `proba = model.predict_proba(df)`
> **Type:** Assignment/comparison

### Line  63
> **Code:** `prob = float(proba[0][1])`
> **Type:** Assignment/comparison

### Line  64
> **Code:** `pred_label = "failure" if prob >= 0.5 else "no_failure"`
> **Type:** Assignment/comparison

### Line  65
> **Code:** `except Exception as exc:`
> **Type:** Code statement

### Line  66
> **Code:** `logger.exception("Prediction failed: %s", exc)`
> **Type:** Arithmetic operation

### Line  67
> **Code:** `raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}...`
> **Type:** Raises an exception

### Line  68
> **Code:** ``
> **Type:** Empty line

### Line  69
> **Code:** `latency_ms = (time.perf_counter() - start) * 1000`
> **Type:** Assignment/comparison

### Line  70
> **Code:** `risk = _risk_level(prob)`
> **Type:** Assignment/comparison

### Line  71
> **Code:** ``
> **Type:** Empty line

### Line  72
> **Code:** `try:`
> **Type:** Code statement

### Line  73
> **Code:** `log = PredictionLog(`
> **Type:** Assignment/comparison

### Line  74
> **Code:** `input_payload=input_dict,`
> **Type:** Assignment/comparison

### Line  75
> **Code:** `prediction=pred_label,`
> **Type:** Assignment/comparison

### Line  76
> **Code:** `probability=prob,`
> **Type:** Assignment/comparison

### Line  77
> **Code:** `model_name=meta.get("name"),`
> **Type:** Assignment/comparison

### Line  78
> **Code:** `model_version=meta.get("version"),`
> **Type:** Assignment/comparison

### Line  79
> **Code:** `model_stage=meta.get("stage"),`
> **Type:** Assignment/comparison

### Line  80
> **Code:** `latency_ms=latency_ms,`
> **Type:** Assignment/comparison

### Line  81
> **Code:** `)`
> **Type:** Code statement

### Line  82
> **Code:** `db.add(log)`
> **Type:** Function call

### Line  83
> **Code:** `db.commit()`
> **Type:** Function call

### Line  84
> **Code:** `except Exception as exc:`
> **Type:** Code statement

### Line  85
> **Code:** `logger.warning("Failed to log prediction to DB: %s", exc)`
> **Type:** Arithmetic operation

### Line  86
> **Code:** `db.rollback()`
> **Type:** Function call

### Line  87
> **Code:** ``
> **Type:** Empty line

### Line  88
> **Code:** `logger.info(`
> **Type:** Code statement

### Line  89
> **Code:** `"Prediction: %s (p=%.4f, risk=%s, latency=%.1fms, model=v%s/%s)",`
> **Type:** Assignment/comparison

### Line  90
> **Code:** `pred_label,`
> **Type:** Code statement

### Line  91
> **Code:** `prob,`
> **Type:** Code statement

### Line  92
> **Code:** `risk,`
> **Type:** Code statement

### Line  93
> **Code:** `latency_ms,`
> **Type:** Code statement

### Line  94
> **Code:** `meta.get("version"),`
> **Type:** Code statement

### Line  95
> **Code:** `meta.get("stage"),`
> **Type:** Code statement

### Line  96
> **Code:** `)`
> **Type:** Code statement

### Line  97
> **Code:** ``
> **Type:** Empty line

### Line  98
> **Code:** `return PredictResponse(`
> **Type:** Returns a value from a function

### Line  99
> **Code:** `prediction=pred_label,`
> **Type:** Assignment/comparison

### Line 100
> **Code:** `probability=prob,`
> **Type:** Assignment/comparison

### Line 101
> **Code:** `risk_level=risk,`
> **Type:** Assignment/comparison

### Line 102
> **Code:** `model_version=str(meta.get("version", "unknown")),`
> **Type:** Assignment/comparison

### Line 103
> **Code:** `model_stage=meta.get("stage", "unknown"),`
> **Type:** Assignment/comparison

### Line 104
> **Code:** `)`
> **Type:** Code statement

## Summary
- **Total lines:** 104
- **Code lines:** 81
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 20

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: predict.py*
---

# mlops-platform-spec-detailed: evaluate.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/ml/evaluation/evaluate.py`
- **Total lines:** 103
- **File size:** 3613 bytes

## Line Type Summary
- **Code:** 74
- **Comment:** 2
- **Empty:** 24
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: high - Add quality gate with thresholds`
> **Type:** TODO: high - Add quality gate with thresholds

### Line   2
> **Code:** `# TODO: medium - Implement comparison vs current production model`
> **Type:** TODO: medium - Implement comparison vs current production model

### Line   3
> **Code:** `# TODO: low - Add metrics export for Evidence Pack`
> **Type:** TODO: low - Add metrics export for Evidence Pack

### Line   4
> **Code:** `"""Evaluate the predictive maintenance model on real AI4I 2020 data.`
> **Type:** Code statement

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `Loads the registered model from MLflow, computes AUC, F1, recall,`
> **Type:** Code statement

### Line   7
> **Code:** `and gates on AUC >= 0.75, F1 >= 0.30 (real data is harder).`
> **Type:** Assignment/comparison

### Line   8
> **Code:** `"""`
> **Type:** Code statement

### Line   9
> **Code:** ``
> **Type:** Empty line

### Line  10
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `import logging`
> **Type:** Imports a module

### Line  13
> **Code:** `import os`
> **Type:** Imports a module

### Line  14
> **Code:** `import sys`
> **Type:** Imports a module

### Line  15
> **Code:** ``
> **Type:** Empty line

### Line  16
> **Code:** `import mlflow`
> **Type:** Imports a module

### Line  17
> **Code:** `import numpy as np`
> **Type:** Imports a module

### Line  18
> **Code:** `from sklearn.metrics import classification_report, f1_score, roc_auc_s...`
> **Type:** Imports specific names from a module

### Line  19
> **Code:** ``
> **Type:** Empty line

### Line  20
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  21
> **Code:** ``
> **Type:** Empty line

### Line  22
> **Code:** `sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "trai...`
> **Type:** Function call

### Line  23
> **Code:** `from preprocess import load_and_preprocess, load_config`
> **Type:** Imports specific names from a module

### Line  24
> **Code:** ``
> **Type:** Empty line

### Line  25
> **Code:** `CONFIG = load_config()`
> **Type:** Assignment/comparison

### Line  26
> **Code:** `MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME", CONFIG["mlflow"]["mod...`
> **Type:** Assignment/comparison

### Line  27
> **Code:** `AUC_THRESHOLD = 0.75`
> **Type:** Assignment/comparison

### Line  28
> **Code:** `F1_THRESHOLD = 0.30`
> **Type:** Assignment/comparison

### Line  29
> **Code:** `MAX_F1_REGRESSION = float(CONFIG.get("evaluation", {}).get("max_f1_reg...`
> **Type:** Assignment/comparison

### Line  30
> **Code:** ``
> **Type:** Empty line

### Line  31
> **Code:** ``
> **Type:** Empty line

### Line  32
> **Code:** `def _production_f1(client, eval_model="Production"):`
> **Type:** Function definition

### Line  33
> **Code:** `"""Fetch the currently deployed model's logged F1 (the bar the candida...`
> **Type:** Logical operation

### Line  34
> **Code:** `must beat within tolerance). Returns None if no production model exist...`
> **Type:** Code statement

### Line  35
> **Code:** `prod = client.get_latest_versions(MODEL_NAME, stages=[eval_model])`
> **Type:** Assignment/comparison

### Line  36
> **Code:** `if not prod:`
> **Type:** Conditional statement

### Line  37
> **Code:** `return None`
> **Type:** Returns a value from a function

### Line  38
> **Code:** `run = client.get_run(prod[0].run_id)`
> **Type:** Assignment/comparison

### Line  39
> **Code:** `f1 = run.data.metrics.get("f1_score") or run.data.metrics.get("f1")`
> **Type:** Assignment/comparison

### Line  40
> **Code:** `if f1 is None:`
> **Type:** Conditional statement

### Line  41
> **Code:** `return None`
> **Type:** Returns a value from a function

### Line  42
> **Code:** `return float(f1)`
> **Type:** Returns a value from a function

### Line  43
> **Code:** ``
> **Type:** Empty line

### Line  44
> **Code:** ``
> **Type:** Empty line

### Line  45
> **Code:** `def main():`
> **Type:** Function definition

### Line  46
> **Code:** `logging.basicConfig(level=logging.INFO)`
> **Type:** Assignment/comparison

### Line  47
> **Code:** ``
> **Type:** Empty line

### Line  48
> **Code:** `tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", CONFIG["mlflow"][...`
> **Type:** Assignment/comparison

### Line  49
> **Code:** `mlflow.set_tracking_uri(tracking_uri)`
> **Type:** Function call

### Line  50
> **Code:** ``
> **Type:** Empty line

### Line  51
> **Code:** `client = mlflow.MlflowClient()`
> **Type:** Assignment/comparison

### Line  52
> **Code:** `versions = client.get_latest_versions(MODEL_NAME, stages=["Production"...`
> **Type:** Assignment/comparison

### Line  53
> **Code:** `if not versions:`
> **Type:** Conditional statement

### Line  54
> **Code:** `logger.error("No registered model found: %s", MODEL_NAME)`
> **Type:** Arithmetic operation

### Line  55
> **Code:** `sys.exit(1)`
> **Type:** Function call

### Line  56
> **Code:** ``
> **Type:** Empty line

### Line  57
> **Code:** `version = versions[0]`
> **Type:** Assignment/comparison

### Line  58
> **Code:** `model_uri = f"models:/{MODEL_NAME}/{version.version}"`
> **Type:** Assignment/comparison

### Line  59
> **Code:** `logger.info("Evaluating %s v%s", MODEL_NAME, version.version)`
> **Type:** Arithmetic operation

### Line  60
> **Code:** ``
> **Type:** Empty line

### Line  61
> **Code:** `clf = mlflow.sklearn.load_model(model_uri)`
> **Type:** Assignment/comparison

### Line  62
> **Code:** ``
> **Type:** Empty line

### Line  63
> **Code:** `X_train, X_test, y_train, y_test = load_and_preprocess()`
> **Type:** Assignment/comparison

### Line  64
> **Code:** ``
> **Type:** Empty line

### Line  65
> **Code:** `proba = clf.predict_proba(X_test)[:, 1]`
> **Type:** Assignment/comparison

### Line  66
> **Code:** `preds = clf.predict(X_test)`
> **Type:** Assignment/comparison

### Line  67
> **Code:** ``
> **Type:** Empty line

### Line  68
> **Code:** `f1 = float(f1_score(y_test, preds, zero_division=0))`
> **Type:** Assignment/comparison

### Line  69
> **Code:** `auc = float(roc_auc_score(y_test, proba))`
> **Type:** Assignment/comparison

### Line  70
> **Code:** `recall = float(np.sum((preds == 1) & (y_test == 1)) / max(np.sum(y_tes...`
> **Type:** Assignment/comparison

### Line  71
> **Code:** ``
> **Type:** Empty line

### Line  72
> **Code:** `print(classification_report(y_test, preds, target_names=["No Failure",...`
> **Type:** Prints output to console

### Line  73
> **Code:** `print(f"AUC:  {auc:.4f}  (threshold: {AUC_THRESHOLD})")`
> **Type:** Prints output to console

### Line  74
> **Code:** `print(f"F1:   {f1:.4f}  (threshold: {F1_THRESHOLD})")`
> **Type:** Prints output to console

### Line  75
> **Code:** `print(f"Recall: {recall:.4f}")`
> **Type:** Prints output to console

### Line  76
> **Code:** ``
> **Type:** Empty line

### Line  77
> **Code:** `# Regression gate vs current Production model (matches config.yml's`
> **Type:** Comment: Regression gate vs current Production model (matches config.yml's

### Line  78
> **Code:** `# evaluation.max_f1_regression and the documented train.sh behavior).`
> **Type:** Comment: evaluation.max_f1_regression and the documented train.sh behavior).

### Line  79
> **Code:** `prod_f1 = _production_f1(client)`
> **Type:** Assignment/comparison

### Line  80
> **Code:** `if prod_f1 is not None:`
> **Type:** Conditional statement

### Line  81
> **Code:** `print(f"Production F1: {prod_f1:.4f}  (tolerance: {MAX_F1_REGRESSION})...`
> **Type:** Prints output to console

### Line  82
> **Code:** `if f1 < prod_f1 - MAX_F1_REGRESSION:`
> **Type:** Conditional statement

### Line  83
> **Code:** `print(`
> **Type:** Prints output to console

### Line  84
> **Code:** `f"FAIL: candidate F1 {f1:.4f} regressed >{MAX_F1_REGRESSION} "`
> **Type:** Comparison operation

### Line  85
> **Code:** `f"below production F1 {prod_f1:.4f}"`
> **Type:** Code statement

### Line  86
> **Code:** `)`
> **Type:** Code statement

### Line  87
> **Code:** `sys.exit(1)`
> **Type:** Function call

### Line  88
> **Code:** `else:`
> **Type:** Else block

### Line  89
> **Code:** `print("No Production model yet; skipping regression gate")`
> **Type:** Prints output to console

### Line  90
> **Code:** ``
> **Type:** Empty line

### Line  91
> **Code:** `if auc < AUC_THRESHOLD:`
> **Type:** Conditional statement

### Line  92
> **Code:** `print(f"FAIL: AUC {auc:.4f} < {AUC_THRESHOLD}")`
> **Type:** Prints output to console

### Line  93
> **Code:** `sys.exit(1)`
> **Type:** Function call

### Line  94
> **Code:** `if f1 < F1_THRESHOLD:`
> **Type:** Conditional statement

### Line  95
> **Code:** `print(f"FAIL: F1 {f1:.4f} < {F1_THRESHOLD}")`
> **Type:** Prints output to console

### Line  96
> **Code:** `sys.exit(1)`
> **Type:** Function call

### Line  97
> **Code:** ``
> **Type:** Empty line

### Line  98
> **Code:** `print(f"PASS: AUC={auc:.4f} >= {AUC_THRESHOLD}, F1={f1:.4f} >= {F1_THR...`
> **Type:** Prints output to console

### Line  99
> **Code:** `sys.exit(0)`
> **Type:** Function call

### Line 100
> **Code:** ``
> **Type:** Empty line

### Line 101
> **Code:** ``
> **Type:** Empty line

### Line 102
> **Code:** `if __name__ == "__main__":`
> **Type:** Conditional statement

### Line 103
> **Code:** `main()`
> **Type:** Function call

## Summary
- **Total lines:** 103
- **Code lines:** 74
- **Comments:** 2
- **TODO items:** 3
- **Empty lines:** 24

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: evaluate.py*
---

# mlops-platform-spec-detailed: preprocess.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/ml/training/preprocess.py`
- **Total lines:** 143
- **File size:** 4698 bytes

## Line Type Summary
- **Code:** 104
- **Comment:** 0
- **Empty:** 36
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: high - Add data validation before training`
> **Type:** TODO: high - Add data validation before training

### Line   2
> **Code:** `# TODO: medium - Implement hyperparameter logging`
> **Type:** TODO: medium - Implement hyperparameter logging

### Line   3
> **Code:** `# TODO: low - Add model explainability integration`
> **Type:** TODO: low - Add model explainability integration

### Line   4
> **Code:** `"""Data loading, validation and preprocessing for the predictive maint...`
> **Type:** Logical operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `Real AI4I 2020 data: equipment_type (L/M/H), sensor readings, binary f...`
> **Type:** Arithmetic operation

### Line   7
> **Code:** `"""`
> **Type:** Code statement

### Line   8
> **Code:** ``
> **Type:** Empty line

### Line   9
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  10
> **Code:** ``
> **Type:** Empty line

### Line  11
> **Code:** `import logging`
> **Type:** Imports a module

### Line  12
> **Code:** `import os`
> **Type:** Imports a module

### Line  13
> **Code:** `from typing import Any`
> **Type:** Imports specific names from a module

### Line  14
> **Code:** ``
> **Type:** Empty line

### Line  15
> **Code:** `import joblib`
> **Type:** Imports a module

### Line  16
> **Code:** `import pandas as pd`
> **Type:** Imports a module

### Line  17
> **Code:** `import yaml`
> **Type:** Imports a module

### Line  18
> **Code:** `from sklearn.model_selection import train_test_split`
> **Type:** Imports specific names from a module

### Line  19
> **Code:** `from sklearn.preprocessing import LabelEncoder, StandardScaler`
> **Type:** Imports specific names from a module

### Line  20
> **Code:** ``
> **Type:** Empty line

### Line  21
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yml")`
> **Type:** Assignment/comparison

### Line  24
> **Code:** ``
> **Type:** Empty line

### Line  25
> **Code:** ``
> **Type:** Empty line

### Line  26
> **Code:** `def load_config() -> dict:`
> **Type:** Function definition

### Line  27
> **Code:** `with open(CONFIG_PATH) as f:`
> **Type:** Context manager

### Line  28
> **Code:** `return yaml.safe_load(f)`
> **Type:** Returns a value from a function

### Line  29
> **Code:** ``
> **Type:** Empty line

### Line  30
> **Code:** ``
> **Type:** Empty line

### Line  31
> **Code:** `def load_raw(path: str | None = None) -> pd.DataFrame:`
> **Type:** Function definition

### Line  32
> **Code:** `config = load_config()`
> **Type:** Assignment/comparison

### Line  33
> **Code:** `path = path or config["data"]["raw_path"]`
> **Type:** Assignment/comparison

### Line  34
> **Code:** `df = pd.read_csv(path)`
> **Type:** Assignment/comparison

### Line  35
> **Code:** `logger.info("Loaded raw data: %s rows x %s cols from %s", len(df), len...`
> **Type:** Arithmetic operation

### Line  36
> **Code:** `return df`
> **Type:** Returns a value from a function

### Line  37
> **Code:** ``
> **Type:** Empty line

### Line  38
> **Code:** ``
> **Type:** Empty line

### Line  39
> **Code:** `def validate_schema(df: pd.DataFrame) -> None:`
> **Type:** Function definition

### Line  40
> **Code:** `config = load_config()`
> **Type:** Assignment/comparison

### Line  41
> **Code:** `target = config["data"]["target"]`
> **Type:** Assignment/comparison

### Line  42
> **Code:** `required = config["features"]["numeric"] + config["features"]["categor...`
> **Type:** Assignment/comparison

### Line  43
> **Code:** `missing = [c for c in required if c not in df.columns]`
> **Type:** Assignment/comparison

### Line  44
> **Code:** `if missing:`
> **Type:** Conditional statement

### Line  45
> **Code:** `raise ValueError(f"Missing columns: {missing}")`
> **Type:** Raises an exception

### Line  46
> **Code:** `logger.info("Schema validation passed")`
> **Type:** Function call

### Line  47
> **Code:** ``
> **Type:** Empty line

### Line  48
> **Code:** ``
> **Type:** Empty line

### Line  49
> **Code:** `def impute(df: pd.DataFrame) -> pd.DataFrame:`
> **Type:** Function definition

### Line  50
> **Code:** `for col in df.select_dtypes(include="number").columns:`
> **Type:** For loop

### Line  51
> **Code:** `df[col] = df[col].fillna(df[col].median())`
> **Type:** Assignment/comparison

### Line  52
> **Code:** `for col in df.select_dtypes(include="object").columns:`
> **Type:** For loop

### Line  53
> **Code:** `df[col] = df[col].fillna("unknown")`
> **Type:** Assignment/comparison

### Line  54
> **Code:** `return df`
> **Type:** Returns a value from a function

### Line  55
> **Code:** ``
> **Type:** Empty line

### Line  56
> **Code:** ``
> **Type:** Empty line

### Line  57
> **Code:** `def encode_target(df: pd.DataFrame) -> pd.DataFrame:`
> **Type:** Function definition

### Line  58
> **Code:** `config = load_config()`
> **Type:** Assignment/comparison

### Line  59
> **Code:** `target = config["data"]["target"]`
> **Type:** Assignment/comparison

### Line  60
> **Code:** `df[target] = df[target].astype(int)`
> **Type:** Assignment/comparison

### Line  61
> **Code:** `return df`
> **Type:** Returns a value from a function

### Line  62
> **Code:** ``
> **Type:** Empty line

### Line  63
> **Code:** ``
> **Type:** Empty line

### Line  64
> **Code:** `def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:`
> **Type:** Function definition

### Line  65
> **Code:** `for col in df.select_dtypes(include="object").columns:`
> **Type:** For loop

### Line  66
> **Code:** `df[col] = df[col].str.strip().str.upper()`
> **Type:** Assignment/comparison

### Line  67
> **Code:** `return df`
> **Type:** Returns a value from a function

### Line  68
> **Code:** ``
> **Type:** Empty line

### Line  69
> **Code:** ``
> **Type:** Empty line

### Line  70
> **Code:** `def load_and_preprocess(`
> **Type:** Function definition

### Line  71
> **Code:** `raw_path: str | None = None,`
> **Type:** Assignment/comparison

### Line  72
> **Code:** `config: dict[str, Any] | None = None,`
> **Type:** Assignment/comparison

### Line  73
> **Code:** `save_processed: str | None = None,`
> **Type:** Assignment/comparison

### Line  74
> **Code:** `save_encoders: str | None = None,`
> **Type:** Assignment/comparison

### Line  75
> **Code:** `) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:`
> **Type:** Arithmetic operation

### Line  76
> **Code:** `config = config or load_config()`
> **Type:** Assignment/comparison

### Line  77
> **Code:** `raw_path = raw_path or config["data"]["raw_path"]`
> **Type:** Assignment/comparison

### Line  78
> **Code:** `test_size = config["data"]["test_size"]`
> **Type:** Assignment/comparison

### Line  79
> **Code:** `random_state = config["data"]["random_state"]`
> **Type:** Assignment/comparison

### Line  80
> **Code:** `target = config["data"]["target"]`
> **Type:** Assignment/comparison

### Line  81
> **Code:** ``
> **Type:** Empty line

### Line  82
> **Code:** `df = pd.read_csv(raw_path)`
> **Type:** Assignment/comparison

### Line  83
> **Code:** `validate_schema(df)`
> **Type:** Function call

### Line  84
> **Code:** `df = normalize_categories(df)`
> **Type:** Assignment/comparison

### Line  85
> **Code:** `df = impute(df)`
> **Type:** Assignment/comparison

### Line  86
> **Code:** `df = encode_target(df)`
> **Type:** Assignment/comparison

### Line  87
> **Code:** ``
> **Type:** Empty line

### Line  88
> **Code:** `feature_cols = config["features"]["numeric"] + config["features"]["cat...`
> **Type:** Assignment/comparison

### Line  89
> **Code:** `X = df[feature_cols]`
> **Type:** Assignment/comparison

### Line  90
> **Code:** `y = df[target]`
> **Type:** Assignment/comparison

### Line  91
> **Code:** ``
> **Type:** Empty line

### Line  92
> **Code:** `encoders = {}`
> **Type:** Assignment/comparison

### Line  93
> **Code:** `for col in X.select_dtypes(include="object").columns:`
> **Type:** For loop

### Line  94
> **Code:** `le = LabelEncoder()`
> **Type:** Assignment/comparison

### Line  95
> **Code:** `X[col] = le.fit_transform(X[col].astype(str))`
> **Type:** Assignment/comparison

### Line  96
> **Code:** `encoders[col] = le`
> **Type:** Assignment/comparison

### Line  97
> **Code:** `logger.info("Encoded categorical: %s -> %d classes", col, len(le.class...`
> **Type:** Arithmetic operation

### Line  98
> **Code:** ``
> **Type:** Empty line

### Line  99
> **Code:** `scaler = StandardScaler()`
> **Type:** Assignment/comparison

### Line 100
> **Code:** `numeric_cols = X.select_dtypes(include="number").columns.tolist()`
> **Type:** Assignment/comparison

### Line 101
> **Code:** `X[numeric_cols] = scaler.fit_transform(X[numeric_cols])`
> **Type:** Assignment/comparison

### Line 102
> **Code:** `encoders["scaler"] = scaler`
> **Type:** Assignment/comparison

### Line 103
> **Code:** `encoders["numeric_cols"] = numeric_cols`
> **Type:** Assignment/comparison

### Line 104
> **Code:** ``
> **Type:** Empty line

### Line 105
> **Code:** `y = df[target]`
> **Type:** Assignment/comparison

### Line 106
> **Code:** ``
> **Type:** Empty line

### Line 107
> **Code:** `X_train, X_test, y_train, y_test = train_test_split(`
> **Type:** Assignment/comparison

### Line 108
> **Code:** `X, y, test_size=test_size, random_state=random_state, stratify=y,`
> **Type:** Assignment/comparison

### Line 109
> **Code:** `)`
> **Type:** Code statement

### Line 110
> **Code:** ``
> **Type:** Empty line

### Line 111
> **Code:** `if save_processed:`
> **Type:** Conditional statement

### Line 112
> **Code:** `os.makedirs(os.path.dirname(save_processed), exist_ok=True)`
> **Type:** Assignment/comparison

### Line 113
> **Code:** `X_train.assign(**{target: y_train}).to_csv(save_processed, index=False...`
> **Type:** Assignment/comparison

### Line 114
> **Code:** `logger.info("Wrote processed train split -> %s", save_processed)`
> **Type:** Arithmetic operation

### Line 115
> **Code:** ``
> **Type:** Empty line

### Line 116
> **Code:** `if save_encoders:`
> **Type:** Conditional statement

### Line 117
> **Code:** `os.makedirs(os.path.dirname(save_encoders), exist_ok=True)`
> **Type:** Assignment/comparison

### Line 118
> **Code:** `joblib.dump(encoders, save_encoders)`
> **Type:** Function call

### Line 119
> **Code:** `logger.info("Saved encoders -> %s", save_encoders)`
> **Type:** Arithmetic operation

### Line 120
> **Code:** ``
> **Type:** Empty line

### Line 121
> **Code:** `logger.info("Train=%d Test=%d", len(X_train), len(X_test))`
> **Type:** Assignment/comparison

### Line 122
> **Code:** `return X_train, X_test, y_train, y_test`
> **Type:** Returns a value from a function

### Line 123
> **Code:** ``
> **Type:** Empty line

### Line 124
> **Code:** ``
> **Type:** Empty line

### Line 125
> **Code:** `def transform_new_data(df: pd.DataFrame, encoders_path: str) -> pd.Dat...`
> **Type:** Function definition

### Line 126
> **Code:** `encoders = joblib.load(encoders_path)`
> **Type:** Assignment/comparison

### Line 127
> **Code:** `df = df.copy()`
> **Type:** Assignment/comparison

### Line 128
> **Code:** ``
> **Type:** Empty line

### Line 129
> **Code:** `for col in df.select_dtypes(include="object").columns:`
> **Type:** For loop

### Line 130
> **Code:** `if col in encoders and isinstance(encoders[col], LabelEncoder):`
> **Type:** Conditional statement

### Line 131
> **Code:** `le = encoders[col]`
> **Type:** Assignment/comparison

### Line 132
> **Code:** `df[col] = df[col].astype(str).map(lambda x: le.transform([x])[0] if x ...`
> **Type:** Assignment/comparison

### Line 133
> **Code:** ``
> **Type:** Empty line

### Line 134
> **Code:** `numeric_cols = encoders.get("numeric_cols", [])`
> **Type:** Assignment/comparison

### Line 135
> **Code:** `if numeric_cols and "scaler" in encoders:`
> **Type:** Conditional statement

### Line 136
> **Code:** `df[numeric_cols] = encoders["scaler"].transform(df[numeric_cols])`
> **Type:** Assignment/comparison

### Line 137
> **Code:** ``
> **Type:** Empty line

### Line 138
> **Code:** `return df`
> **Type:** Returns a value from a function

### Line 139
> **Code:** ``
> **Type:** Empty line

### Line 140
> **Code:** ``
> **Type:** Empty line

### Line 141
> **Code:** `if __name__ == "__main__":`
> **Type:** Conditional statement

### Line 142
> **Code:** `logging.basicConfig(level=logging.INFO)`
> **Type:** Assignment/comparison

### Line 143
> **Code:** `load_and_preprocess()`
> **Type:** Logical operation

## Summary
- **Total lines:** 143
- **Code lines:** 104
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 36

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: preprocess.py*
---

# mlops-platform-spec-detailed: train.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/ml/training/train.py`
- **Total lines:** 123
- **File size:** 4155 bytes

## Line Type Summary
- **Code:** 95
- **Comment:** 0
- **Empty:** 25
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: high - Add data validation before training`
> **Type:** TODO: high - Add data validation before training

### Line   2
> **Code:** `# TODO: medium - Implement hyperparameter logging`
> **Type:** TODO: medium - Implement hyperparameter logging

### Line   3
> **Code:** `# TODO: low - Add model explainability integration`
> **Type:** TODO: low - Add model explainability integration

### Line   4
> **Code:** `"""Train a predictive maintenance model on real AI4I 2020 data and log...`
> **Type:** Logical operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `Steps:`
> **Type:** Code statement

### Line   7
> **Code:** `1. Load maintenance.csv (real data)`
> **Type:** Function call

### Line   8
> **Code:** `2. Preprocess (validate, impute, encode, scale, split)`
> **Type:** Function call

### Line   9
> **Code:** `3. Train RandomForestClassifier with class_weight='balanced'`
> **Type:** Assignment/comparison

### Line  10
> **Code:** `4. Log params + metrics (F1, AUC, recall) to MLflow`
> **Type:** Arithmetic operation

### Line  11
> **Code:** `5. Register model as "maintenance-model"`
> **Type:** Arithmetic operation

### Line  12
> **Code:** `"""`
> **Type:** Code statement

### Line  13
> **Code:** ``
> **Type:** Empty line

### Line  14
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  15
> **Code:** ``
> **Type:** Empty line

### Line  16
> **Code:** `import logging`
> **Type:** Imports a module

### Line  17
> **Code:** `import os`
> **Type:** Imports a module

### Line  18
> **Code:** `import sys`
> **Type:** Imports a module

### Line  19
> **Code:** ``
> **Type:** Empty line

### Line  20
> **Code:** `import mlflow`
> **Type:** Imports a module

### Line  21
> **Code:** `import mlflow.sklearn`
> **Type:** Imports a module

### Line  22
> **Code:** `import numpy as np`
> **Type:** Imports a module

### Line  23
> **Code:** ``
> **Type:** Empty line

### Line  24
> **Code:** `from preprocess import load_and_preprocess, load_config`
> **Type:** Imports specific names from a module

### Line  25
> **Code:** ``
> **Type:** Empty line

### Line  26
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  27
> **Code:** ``
> **Type:** Empty line

### Line  28
> **Code:** `CONFIG = load_config()`
> **Type:** Assignment/comparison

### Line  29
> **Code:** `MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME", CONFIG["mlflow"]["mod...`
> **Type:** Assignment/comparison

### Line  30
> **Code:** ``
> **Type:** Empty line

### Line  31
> **Code:** ``
> **Type:** Empty line

### Line  32
> **Code:** `def train_and_log(`
> **Type:** Function definition

### Line  33
> **Code:** `raw_path: str | None = None,`
> **Type:** Assignment/comparison

### Line  34
> **Code:** `register: bool = True,`
> **Type:** Assignment/comparison

### Line  35
> **Code:** `) -> dict:`
> **Type:** Arithmetic operation

### Line  36
> **Code:** `config = load_config()`
> **Type:** Assignment/comparison

### Line  37
> **Code:** `tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"][...`
> **Type:** Assignment/comparison

### Line  38
> **Code:** `mlflow.set_tracking_uri(tracking_uri)`
> **Type:** Function call

### Line  39
> **Code:** `mlflow.set_experiment(config["mlflow"]["experiment_name"])`
> **Type:** Function call

### Line  40
> **Code:** ``
> **Type:** Empty line

### Line  41
> **Code:** `X_train, X_test, y_train, y_test = load_and_preprocess(`
> **Type:** Assignment/comparison

### Line  42
> **Code:** `raw_path=raw_path,`
> **Type:** Assignment/comparison

### Line  43
> **Code:** `save_processed=config["data"]["processed_file"],`
> **Type:** Assignment/comparison

### Line  44
> **Code:** `save_encoders=config["data"]["encoders_file"],`
> **Type:** Assignment/comparison

### Line  45
> **Code:** `)`
> **Type:** Code statement

### Line  46
> **Code:** ``
> **Type:** Empty line

### Line  47
> **Code:** `params = {`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `"n_estimators": config["model"]["n_estimators"],`
> **Type:** Logical operation

### Line  49
> **Code:** `"max_depth": config["model"]["max_depth"],`
> **Type:** Data structure operation

### Line  50
> **Code:** `"min_samples_split": config["model"]["min_samples_split"],`
> **Type:** Data structure operation

### Line  51
> **Code:** `"min_samples_leaf": config["model"]["min_samples_leaf"],`
> **Type:** Data structure operation

### Line  52
> **Code:** `"max_features": config["model"]["max_features"],`
> **Type:** Data structure operation

### Line  53
> **Code:** `"class_weight": config["model"]["class_weight"],`
> **Type:** Data structure operation

### Line  54
> **Code:** `"random_state": 42,`
> **Type:** Logical operation

### Line  55
> **Code:** `"n_jobs": config["model"]["n_jobs"],`
> **Type:** Data structure operation

### Line  56
> **Code:** `}`
> **Type:** Code statement

### Line  57
> **Code:** ``
> **Type:** Empty line

### Line  58
> **Code:** `from sklearn.ensemble import RandomForestClassifier`
> **Type:** Imports specific names from a module

### Line  59
> **Code:** `from sklearn.metrics import (`
> **Type:** Imports specific names from a module

### Line  60
> **Code:** `classification_report,`
> **Type:** Logical operation

### Line  61
> **Code:** `f1_score,`
> **Type:** Logical operation

### Line  62
> **Code:** `precision_score,`
> **Type:** Logical operation

### Line  63
> **Code:** `recall_score,`
> **Type:** Logical operation

### Line  64
> **Code:** `roc_auc_score,`
> **Type:** Logical operation

### Line  65
> **Code:** `)`
> **Type:** Code statement

### Line  66
> **Code:** ``
> **Type:** Empty line

### Line  67
> **Code:** `clf = RandomForestClassifier(**params)`
> **Type:** Assignment/comparison

### Line  68
> **Code:** `clf.fit(X_train, y_train)`
> **Type:** Function call

### Line  69
> **Code:** ``
> **Type:** Empty line

### Line  70
> **Code:** `proba = clf.predict_proba(X_test)[:, 1]`
> **Type:** Assignment/comparison

### Line  71
> **Code:** `preds = clf.predict(X_test)`
> **Type:** Assignment/comparison

### Line  72
> **Code:** ``
> **Type:** Empty line

### Line  73
> **Code:** `metrics = {`
> **Type:** Assignment/comparison

### Line  74
> **Code:** `"f1": float(f1_score(y_test, preds, zero_division=0)),`
> **Type:** Assignment/comparison

### Line  75
> **Code:** `"precision": float(precision_score(y_test, preds, zero_division=0)),`
> **Type:** Assignment/comparison

### Line  76
> **Code:** `"recall": float(recall_score(y_test, preds, zero_division=0)),`
> **Type:** Assignment/comparison

### Line  77
> **Code:** `"roc_auc": float(roc_auc_score(y_test, proba)),`
> **Type:** Logical operation

### Line  78
> **Code:** `}`
> **Type:** Code statement

### Line  79
> **Code:** ``
> **Type:** Empty line

### Line  80
> **Code:** `logger.info("F1=%.4f AUC=%.4f", metrics["f1"], metrics["roc_auc"])`
> **Type:** Assignment/comparison

### Line  81
> **Code:** `logger.info("\n%s", classification_report(y_test, preds, target_names=...`
> **Type:** Assignment/comparison

### Line  82
> **Code:** ``
> **Type:** Empty line

### Line  83
> **Code:** `with mlflow.start_run() as run:`
> **Type:** Context manager

### Line  84
> **Code:** `mlflow.log_params(params)`
> **Type:** Function call

### Line  85
> **Code:** `mlflow.log_params({`
> **Type:** Code statement

### Line  86
> **Code:** `"n_features": X_train.shape[1],`
> **Type:** Data structure operation

### Line  87
> **Code:** `"data_source": os.path.basename(raw_path or config["data"]["raw_path"]...`
> **Type:** Logical operation

### Line  88
> **Code:** `"failure_rate": f"{y_train.mean():.4f}",`
> **Type:** Code statement

### Line  89
> **Code:** `})`
> **Type:** Code statement

### Line  90
> **Code:** `mlflow.log_metrics(metrics)`
> **Type:** Function call

### Line  91
> **Code:** `mlflow.sklearn.log_model(clf, config["mlflow"]["artifact_path"])`
> **Type:** Function call

### Line  92
> **Code:** ``
> **Type:** Empty line

### Line  93
> **Code:** `if register:`
> **Type:** Conditional statement

### Line  94
> **Code:** `model_uri = f"runs:/{run.info.run_id}/{config['mlflow']['artifact_path...`
> **Type:** Assignment/comparison

### Line  95
> **Code:** `registered = mlflow.register_model(model_uri, MODEL_NAME)`
> **Type:** Assignment/comparison

### Line  96
> **Code:** `client = mlflow.MlflowClient()`
> **Type:** Assignment/comparison

### Line  97
> **Code:** `client.transition_model_version_stage(`
> **Type:** Code statement

### Line  98
> **Code:** `name=MODEL_NAME, version=registered.version, stage="Staging"`
> **Type:** Assignment/comparison

### Line  99
> **Code:** `)`
> **Type:** Code statement

### Line 100
> **Code:** `logger.info("Registered %s v%s in Staging", MODEL_NAME, registered.ver...`
> **Type:** Arithmetic operation

### Line 101
> **Code:** ``
> **Type:** Empty line

### Line 102
> **Code:** `return {"metrics": metrics, "run_id": run.info.run_id}`
> **Type:** Returns a value from a function

### Line 103
> **Code:** ``
> **Type:** Empty line

### Line 104
> **Code:** ``
> **Type:** Empty line

### Line 105
> **Code:** `def main():`
> **Type:** Function definition

### Line 106
> **Code:** `import argparse`
> **Type:** Imports a module

### Line 107
> **Code:** ``
> **Type:** Empty line

### Line 108
> **Code:** `logging.basicConfig(level=logging.INFO)`
> **Type:** Assignment/comparison

### Line 109
> **Code:** `parser = argparse.ArgumentParser()`
> **Type:** Assignment/comparison

### Line 110
> **Code:** `parser.add_argument("--raw-path", default=None)`
> **Type:** Assignment/comparison

### Line 111
> **Code:** `parser.add_argument("--register", action="store_true")`
> **Type:** Assignment/comparison

### Line 112
> **Code:** `args = parser.parse_args()`
> **Type:** Assignment/comparison

### Line 113
> **Code:** ``
> **Type:** Empty line

### Line 114
> **Code:** `try:`
> **Type:** Code statement

### Line 115
> **Code:** `result = train_and_log(raw_path=args.raw_path, register=args.register)`
> **Type:** Assignment/comparison

### Line 116
> **Code:** `print(f"Training done. F1={result['metrics']['f1']:.4f} AUC={result['m...`
> **Type:** Prints output to console

### Line 117
> **Code:** `except Exception as e:`
> **Type:** Code statement

### Line 118
> **Code:** `logger.exception("Training failed: %s", e)`
> **Type:** Arithmetic operation

### Line 119
> **Code:** `sys.exit(1)`
> **Type:** Function call

### Line 120
> **Code:** ``
> **Type:** Empty line

### Line 121
> **Code:** ``
> **Type:** Empty line

### Line 122
> **Code:** `if __name__ == "__main__":`
> **Type:** Conditional statement

### Line 123
> **Code:** `main()`
> **Type:** Function call

## Summary
- **Total lines:** 123
- **Code lines:** 95
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 25

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: train.py*
---

# mlops-platform-spec-detailed: features.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/ml/training/features.py`
- **Total lines:** 75
- **File size:** 2472 bytes

## Line Type Summary
- **Code:** 54
- **Comment:** 0
- **Empty:** 18
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: high - Add data validation before training`
> **Type:** TODO: high - Add data validation before training

### Line   2
> **Code:** `# TODO: medium - Implement hyperparameter logging`
> **Type:** TODO: medium - Implement hyperparameter logging

### Line   3
> **Code:** `# TODO: low - Add model explainability integration`
> **Type:** TODO: low - Add model explainability integration

### Line   4
> **Code:** `"""Feature engineering for the predictive maintenance pipeline.`
> **Type:** Logical operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `Builds the sklearn feature preprocessor used both by training and eval...`
> **Type:** Logical operation

### Line   7
> **Code:** `The pipeline one-hot encodes categoricals (handle_unknown='ignore' so ...`
> **Type:** Assignment/comparison

### Line   8
> **Code:** `serving layer can send unseen values safely) and passes numerics throu...`
> **Type:** Logical operation

### Line   9
> **Code:** `Column lists come from ml/training/config.yml (numeric + categorical);...`
> **Type:** Arithmetic operation

### Line  10
> **Code:** `preprocessor is schema-agnostic.`
> **Type:** Arithmetic operation

### Line  11
> **Code:** `"""`
> **Type:** Code statement

### Line  12
> **Code:** ``
> **Type:** Empty line

### Line  13
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  14
> **Code:** ``
> **Type:** Empty line

### Line  15
> **Code:** `import logging`
> **Type:** Imports a module

### Line  16
> **Code:** `from typing import Any`
> **Type:** Imports specific names from a module

### Line  17
> **Code:** ``
> **Type:** Empty line

### Line  18
> **Code:** `import pandas as pd`
> **Type:** Imports a module

### Line  19
> **Code:** `from sklearn.compose import ColumnTransformer`
> **Type:** Imports specific names from a module

### Line  20
> **Code:** `from sklearn.pipeline import Pipeline`
> **Type:** Imports specific names from a module

### Line  21
> **Code:** `from sklearn.preprocessing import OneHotEncoder, StandardScaler`
> **Type:** Imports specific names from a module

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  24
> **Code:** ``
> **Type:** Empty line

### Line  25
> **Code:** `DROP_COLUMNS = ["customer_id"]`
> **Type:** Assignment/comparison

### Line  26
> **Code:** ``
> **Type:** Empty line

### Line  27
> **Code:** ``
> **Type:** Empty line

### Line  28
> **Code:** `def expected_columns(numeric: list[str], categorical: list[str]) -> li...`
> **Type:** Function definition

### Line  29
> **Code:** `"""Column names the serving API must send in each /predict payload."""`
> **Type:** Arithmetic operation

### Line  30
> **Code:** `return numeric + categorical`
> **Type:** Returns a value from a function

### Line  31
> **Code:** ``
> **Type:** Empty line

### Line  32
> **Code:** ``
> **Type:** Empty line

### Line  33
> **Code:** `def drop_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:`
> **Type:** Function definition

### Line  34
> **Code:** `"""Remove identifier columns not used as features."""`
> **Type:** Logical operation

### Line  35
> **Code:** `drop = [c for c in DROP_COLUMNS if c in df.columns]`
> **Type:** Assignment/comparison

### Line  36
> **Code:** `if drop:`
> **Type:** Conditional statement

### Line  37
> **Code:** `logger.info("Dropping metadata columns: %s", drop)`
> **Type:** Arithmetic operation

### Line  38
> **Code:** `return df.drop(columns=drop)`
> **Type:** Returns a value from a function

### Line  39
> **Code:** ``
> **Type:** Empty line

### Line  40
> **Code:** ``
> **Type:** Empty line

### Line  41
> **Code:** `def build_preprocessor(`
> **Type:** Function definition

### Line  42
> **Code:** `numeric: list[str], categorical: list[str], scale: bool = True`
> **Type:** Assignment/comparison

### Line  43
> **Code:** `) -> ColumnTransformer:`
> **Type:** Arithmetic operation

### Line  44
> **Code:** `"""ColumnTransformer: passthrough numerics, one-hot categoricals."""`
> **Type:** Arithmetic operation

### Line  45
> **Code:** `transformers: list[tuple[str, Any, list[str]]] = []`
> **Type:** Assignment/comparison

### Line  46
> **Code:** ``
> **Type:** Empty line

### Line  47
> **Code:** `numeric_present = [c for c in numeric if True]`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `if numeric_present:`
> **Type:** Conditional statement

### Line  49
> **Code:** `steps = [("scaler", StandardScaler())] if scale else []`
> **Type:** Assignment/comparison

### Line  50
> **Code:** `transformers.append(`
> **Type:** Logical operation

### Line  51
> **Code:** `(`
> **Type:** Code statement

### Line  52
> **Code:** `"num",`
> **Type:** Code statement

### Line  53
> **Code:** `Pipeline(steps) if steps else "passthrough",`
> **Type:** Code statement

### Line  54
> **Code:** `numeric_present,`
> **Type:** Code statement

### Line  55
> **Code:** `)`
> **Type:** Code statement

### Line  56
> **Code:** `)`
> **Type:** Code statement

### Line  57
> **Code:** ``
> **Type:** Empty line

### Line  58
> **Code:** `if categorical:`
> **Type:** Conditional statement

### Line  59
> **Code:** `transformers.append(`
> **Type:** Logical operation

### Line  60
> **Code:** `(`
> **Type:** Code statement

### Line  61
> **Code:** `"cat",`
> **Type:** Code statement

### Line  62
> **Code:** `OneHotEncoder(handle_unknown="ignore", sparse_output=False),`
> **Type:** Assignment/comparison

### Line  63
> **Code:** `categorical,`
> **Type:** Logical operation

### Line  64
> **Code:** `)`
> **Type:** Code statement

### Line  65
> **Code:** `)`
> **Type:** Code statement

### Line  66
> **Code:** ``
> **Type:** Empty line

### Line  67
> **Code:** `if not transformers:`
> **Type:** Conditional statement

### Line  68
> **Code:** `raise ValueError("No features configured for the preprocessor.")`
> **Type:** Raises an exception

### Line  69
> **Code:** ``
> **Type:** Empty line

### Line  70
> **Code:** `return ColumnTransformer(transformers, remainder="drop")`
> **Type:** Returns a value from a function

### Line  71
> **Code:** ``
> **Type:** Empty line

### Line  72
> **Code:** ``
> **Type:** Empty line

### Line  73
> **Code:** `def build_feature_columns(numeric: list[str], categorical: list[str]) ...`
> **Type:** Function definition

### Line  74
> **Code:** `"""Ordered feature columns expected by the trained model."""`
> **Type:** Code statement

### Line  75
> **Code:** `return numeric + categorical`
> **Type:** Returns a value from a function

## Summary
- **Total lines:** 75
- **Code lines:** 54
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 18

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: features.py*
---

# mlops-platform-spec-detailed: drift_detector.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/ml/monitoring/drift_detector.py`
- **Total lines:** 116
- **File size:** 3855 bytes

## Line Type Summary
- **Code:** 88
- **Comment:** 1
- **Empty:** 24
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: high - Add alert rule for ingestion stalls`
> **Type:** TODO: high - Add alert rule for ingestion stalls

### Line   2
> **Code:** `# TODO: medium - Implement dashboard for drift detection`
> **Type:** TODO: medium - Implement dashboard for drift detection

### Line   3
> **Code:** `# TODO: low - Add prediction distribution monitoring`
> **Type:** TODO: low - Add prediction distribution monitoring

### Line   4
> **Code:** `"""Data drift detection for the predictive maintenance pipeline.`
> **Type:** Logical operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `Compares the current/inference data distribution against the reference`
> **Type:** Arithmetic operation

### Line   7
> **Code:** `(training) data per numeric feature using a two-sample Kolmogorov-Smir...`
> **Type:** Arithmetic operation

### Line   8
> **Code:** `test. Produces an aggregate drift score (fraction of features that dri...`
> **Type:** Logical operation

### Line   9
> **Code:** `written to ml/data/monitoring/drift_report.json so the retraining trig...`
> **Type:** Arithmetic operation

### Line  10
> **Code:** `consume it.`
> **Type:** Code statement

### Line  11
> **Code:** ``
> **Type:** Empty line

### Line  12
> **Code:** `Numeric feature list and data paths come from ml/training/config.yml.`
> **Type:** Arithmetic operation

### Line  13
> **Code:** `"""`
> **Type:** Code statement

### Line  14
> **Code:** ``
> **Type:** Empty line

### Line  15
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  16
> **Code:** ``
> **Type:** Empty line

### Line  17
> **Code:** `import json`
> **Type:** Imports a module

### Line  18
> **Code:** `import logging`
> **Type:** Imports a module

### Line  19
> **Code:** `import os`
> **Type:** Imports a module

### Line  20
> **Code:** `import sys`
> **Type:** Imports a module

### Line  21
> **Code:** `from pathlib import Path`
> **Type:** Imports specific names from a module

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `import numpy as np`
> **Type:** Imports a module

### Line  24
> **Code:** `import pandas as pd`
> **Type:** Imports a module

### Line  25
> **Code:** `from scipy import stats`
> **Type:** Imports specific names from a module

### Line  26
> **Code:** ``
> **Type:** Empty line

### Line  27
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  28
> **Code:** ``
> **Type:** Empty line

### Line  29
> **Code:** `sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "trai...`
> **Type:** Function call

### Line  30
> **Code:** `from preprocess import load_config`
> **Type:** Imports specific names from a module

### Line  31
> **Code:** ``
> **Type:** Empty line

### Line  32
> **Code:** `CONFIG = load_config()`
> **Type:** Assignment/comparison

### Line  33
> **Code:** `NUMERIC_FEATURES = CONFIG["features"]["numeric"]`
> **Type:** Assignment/comparison

### Line  34
> **Code:** `DEFAULT_RAW_PATH = CONFIG["data"]["raw_path"]`
> **Type:** Assignment/comparison

### Line  35
> **Code:** ``
> **Type:** Empty line

### Line  36
> **Code:** `# Kernel-smoothed reference; current is what inference/production sees...`
> **Type:** Comment: Kernel-smoothed reference; current is what inference/production sees.

### Line  37
> **Code:** `DEFAULT_CURRENT_PATH = Path(CONFIG["data"].get("current_path", "ml/dat...`
> **Type:** Assignment/comparison

### Line  38
> **Code:** `REPORT_PATH = Path("ml/data/monitoring/drift_report.json")`
> **Type:** Assignment/comparison

### Line  39
> **Code:** ``
> **Type:** Empty line

### Line  40
> **Code:** `KS_ALPHA = 0.05`
> **Type:** Assignment/comparison

### Line  41
> **Code:** `KS_STAT_THRESHOLD = 0.1`
> **Type:** Assignment/comparison

### Line  42
> **Code:** `DRIFT_HARD_THRESHOLD = float(`
> **Type:** Assignment/comparison

### Line  43
> **Code:** `os.environ.get("DRIFT_THRESHOLD", CONFIG.get("evaluation", {}).get("dr...`
> **Type:** Function call

### Line  44
> **Code:** `)`
> **Type:** Code statement

### Line  45
> **Code:** ``
> **Type:** Empty line

### Line  46
> **Code:** ``
> **Type:** Empty line

### Line  47
> **Code:** `def _load_numeric(df: pd.DataFrame) -> dict[str, np.ndarray]:`
> **Type:** Function definition

### Line  48
> **Code:** `pdf = df[NUMERIC_FEATURES].apply(pd.to_numeric, errors="coerce")`
> **Type:** Assignment/comparison

### Line  49
> **Code:** `return {col: pdf[col].dropna().to_numpy() for col in NUMERIC_FEATURES}`
> **Type:** Returns a value from a function

### Line  50
> **Code:** ``
> **Type:** Empty line

### Line  51
> **Code:** ``
> **Type:** Empty line

### Line  52
> **Code:** `def detect_drift(`
> **Type:** Function definition

### Line  53
> **Code:** `reference_path: str | Path,`
> **Type:** Code statement

### Line  54
> **Code:** `current_path: str | Path = DEFAULT_CURRENT_PATH,`
> **Type:** Assignment/comparison

### Line  55
> **Code:** `) -> dict:`
> **Type:** Arithmetic operation

### Line  56
> **Code:** `"""Return per-feature KS results plus an aggregate drift score.`
> **Type:** Arithmetic operation

### Line  57
> **Code:** ``
> **Type:** Empty line

### Line  58
> **Code:** `score = fraction of numeric features flagged as drifted.`
> **Type:** Assignment/comparison

### Line  59
> **Code:** `"""`
> **Type:** Code statement

### Line  60
> **Code:** `ref = pd.read_csv(reference_path)`
> **Type:** Assignment/comparison

### Line  61
> **Code:** `cur = pd.read_csv(current_path)`
> **Type:** Assignment/comparison

### Line  62
> **Code:** ``
> **Type:** Empty line

### Line  63
> **Code:** `ref_num = _load_numeric(ref)`
> **Type:** Assignment/comparison

### Line  64
> **Code:** `cur_num = _load_numeric(cur)`
> **Type:** Assignment/comparison

### Line  65
> **Code:** ``
> **Type:** Empty line

### Line  66
> **Code:** `features = {}`
> **Type:** Assignment/comparison

### Line  67
> **Code:** `flagged = []`
> **Type:** Assignment/comparison

### Line  68
> **Code:** `for col in NUMERIC_FEATURES:`
> **Type:** For loop

### Line  69
> **Code:** `if col not in ref_num or col not in cur_num:`
> **Type:** Conditional statement

### Line  70
> **Code:** `features[col] = {"error": "column missing"}`
> **Type:** Assignment/comparison

### Line  71
> **Code:** `continue`
> **Type:** Code statement

### Line  72
> **Code:** `r, c = ref_num[col], cur_num[col]`
> **Type:** Assignment/comparison

### Line  73
> **Code:** `if r.size == 0 or c.size == 0:`
> **Type:** Conditional statement

### Line  74
> **Code:** `features[col] = {"error": "empty column"}`
> **Type:** Assignment/comparison

### Line  75
> **Code:** `continue`
> **Type:** Code statement

### Line  76
> **Code:** `stat, p = stats.ks_2samp(r, c)`
> **Type:** Assignment/comparison

### Line  77
> **Code:** `drifted = bool(p < KS_ALPHA and stat > KS_STAT_THRESHOLD)`
> **Type:** Assignment/comparison

### Line  78
> **Code:** `features[col] = {`
> **Type:** Assignment/comparison

### Line  79
> **Code:** `"ks_statistic": float(stat),`
> **Type:** Code statement

### Line  80
> **Code:** `"p_value": float(p),`
> **Type:** Code statement

### Line  81
> **Code:** `"drifted": drifted,`
> **Type:** Code statement

### Line  82
> **Code:** `}`
> **Type:** Code statement

### Line  83
> **Code:** `if drifted:`
> **Type:** Conditional statement

### Line  84
> **Code:** `flagged.append(col)`
> **Type:** Function call

### Line  85
> **Code:** ``
> **Type:** Empty line

### Line  86
> **Code:** `drift_score = len(set(flagged)) / max(len(NUMERIC_FEATURES), 1)`
> **Type:** Assignment/comparison

### Line  87
> **Code:** ``
> **Type:** Empty line

### Line  88
> **Code:** `report = {`
> **Type:** Assignment/comparison

### Line  89
> **Code:** `"reference_path": str(reference_path),`
> **Type:** Code statement

### Line  90
> **Code:** `"current_path": str(current_path),`
> **Type:** Code statement

### Line  91
> **Code:** `"n_features": len(NUMERIC_FEATURES),`
> **Type:** Code statement

### Line  92
> **Code:** `"drift_score": drift_score,`
> **Type:** Logical operation

### Line  93
> **Code:** `"threshold": DRIFT_HARD_THRESHOLD,`
> **Type:** Code statement

### Line  94
> **Code:** `"drift_detected": drift_score > DRIFT_HARD_THRESHOLD,`
> **Type:** Comparison operation

### Line  95
> **Code:** `"drifted_features": flagged,`
> **Type:** Code statement

### Line  96
> **Code:** `"features": features,`
> **Type:** Code statement

### Line  97
> **Code:** `}`
> **Type:** Code statement

### Line  98
> **Code:** ``
> **Type:** Empty line

### Line  99
> **Code:** `REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)`
> **Type:** Assignment/comparison

### Line 100
> **Code:** `REPORT_PATH.write_text(json.dumps(report, indent=2))`
> **Type:** Assignment/comparison

### Line 101
> **Code:** `logger.info("Drift score=%.3f threshold=%.3f detected=%s", drift_score...`
> **Type:** Assignment/comparison

### Line 102
> **Code:** `return report`
> **Type:** Returns a value from a function

### Line 103
> **Code:** ``
> **Type:** Empty line

### Line 104
> **Code:** ``
> **Type:** Empty line

### Line 105
> **Code:** `def main() -> None:`
> **Type:** Function definition

### Line 106
> **Code:** `logging.basicConfig(level=logging.INFO)`
> **Type:** Assignment/comparison

### Line 107
> **Code:** `parser = __import__("argparse").ArgumentParser(description="Drift dete...`
> **Type:** Assignment/comparison

### Line 108
> **Code:** `parser.add_argument("--reference", default=DEFAULT_RAW_PATH)`
> **Type:** Assignment/comparison

### Line 109
> **Code:** `parser.add_argument("--current", default=str(DEFAULT_CURRENT_PATH))`
> **Type:** Assignment/comparison

### Line 110
> **Code:** `args = parser.parse_args()`
> **Type:** Assignment/comparison

### Line 111
> **Code:** `report = detect_drift(args.reference, args.current)`
> **Type:** Assignment/comparison

### Line 112
> **Code:** `print(json.dumps(report, indent=2))`
> **Type:** Prints output to console

### Line 113
> **Code:** ``
> **Type:** Empty line

### Line 114
> **Code:** ``
> **Type:** Empty line

### Line 115
> **Code:** `if __name__ == "__main__":`
> **Type:** Conditional statement

### Line 116
> **Code:** `main()`
> **Type:** Function call

## Summary
- **Total lines:** 116
- **Code lines:** 88
- **Comments:** 1
- **TODO items:** 3
- **Empty lines:** 24

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: drift_detector.py*
---

# mlops-platform-spec-detailed: retraining_trigger.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/ml/monitoring/retraining_trigger.py`
- **Total lines:** 84
- **File size:** 2916 bytes

## Line Type Summary
- **Code:** 63
- **Comment:** 0
- **Empty:** 18
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `# TODO: high - Add alert rule for ingestion stalls`
> **Type:** TODO: high - Add alert rule for ingestion stalls

### Line   2
> **Code:** `# TODO: medium - Implement dashboard for drift detection`
> **Type:** TODO: medium - Implement dashboard for drift detection

### Line   3
> **Code:** `# TODO: low - Add prediction distribution monitoring`
> **Type:** TODO: low - Add prediction distribution monitoring

### Line   4
> **Code:** `"""Drift-driven automatic retraining trigger for the maintenance pipel...`
> **Type:** Arithmetic operation

### Line   5
> **Code:** ``
> **Type:** Empty line

### Line   6
> **Code:** `Reads the drift report produced by drift_detector.py; when the drift s...`
> **Type:** Logical operation

### Line   7
> **Code:** `exceeds the configured threshold it launches an automatic retrain`
> **Type:** Code statement

### Line   8
> **Code:** `(ml/training/train.py) followed by re-evaluation (ml/evaluation/evalua...`
> **Type:** Arithmetic operation

### Line   9
> **Code:** `Promotion still requires the CI approval gate, so automation never ski...`
> **Type:** Code statement

### Line  10
> **Code:** `human sign-off before Production.`
> **Type:** Arithmetic operation

### Line  11
> **Code:** `"""`
> **Type:** Code statement

### Line  12
> **Code:** ``
> **Type:** Empty line

### Line  13
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  14
> **Code:** ``
> **Type:** Empty line

### Line  15
> **Code:** `import argparse`
> **Type:** Imports a module

### Line  16
> **Code:** `import json`
> **Type:** Imports a module

### Line  17
> **Code:** `import logging`
> **Type:** Imports a module

### Line  18
> **Code:** `import os`
> **Type:** Imports a module

### Line  19
> **Code:** `import subprocess`
> **Type:** Imports a module

### Line  20
> **Code:** `import sys`
> **Type:** Imports a module

### Line  21
> **Code:** `from pathlib import Path`
> **Type:** Imports specific names from a module

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `logger = logging.getLogger(__name__)`
> **Type:** Assignment/comparison

### Line  24
> **Code:** ``
> **Type:** Empty line

### Line  25
> **Code:** `REPORT_PATH = Path("ml/data/monitoring/drift_report.json")`
> **Type:** Assignment/comparison

### Line  26
> **Code:** `REPO_ROOT = Path(__file__).resolve().parents[3]`
> **Type:** Assignment/comparison

### Line  27
> **Code:** `DEFAULT_THRESHOLD = 0.3`
> **Type:** Assignment/comparison

### Line  28
> **Code:** ``
> **Type:** Empty line

### Line  29
> **Code:** ``
> **Type:** Empty line

### Line  30
> **Code:** `def read_drift_report(path: Path = REPORT_PATH) -> dict:`
> **Type:** Function definition

### Line  31
> **Code:** `if not path.exists():`
> **Type:** Conditional statement

### Line  32
> **Code:** `return {"drift_score": 0.0, "threshold": DEFAULT_THRESHOLD, "drift_det...`
> **Type:** Returns a value from a function

### Line  33
> **Code:** `return json.loads(path.read_text())`
> **Type:** Returns a value from a function

### Line  34
> **Code:** ``
> **Type:** Empty line

### Line  35
> **Code:** ``
> **Type:** Empty line

### Line  36
> **Code:** `def should_retrain(report: dict, threshold: float | None = None) -> bo...`
> **Type:** Function definition

### Line  37
> **Code:** `score = float(report.get("drift_score", 0.0))`
> **Type:** Assignment/comparison

### Line  38
> **Code:** `thr = threshold if threshold is not None else float(`
> **Type:** Assignment/comparison

### Line  39
> **Code:** `os.environ.get("DRIFT_THRESHOLD", report.get("threshold", DEFAULT_THRE...`
> **Type:** Logical operation

### Line  40
> **Code:** `)`
> **Type:** Code statement

### Line  41
> **Code:** `return score > thr`
> **Type:** Returns a value from a function

### Line  42
> **Code:** ``
> **Type:** Empty line

### Line  43
> **Code:** ``
> **Type:** Empty line

### Line  44
> **Code:** `def trigger_retraining(dry_run: bool = False) -> dict:`
> **Type:** Function definition

### Line  45
> **Code:** `report = read_drift_report()`
> **Type:** Assignment/comparison

### Line  46
> **Code:** `score = float(report.get("drift_score", 0.0))`
> **Type:** Assignment/comparison

### Line  47
> **Code:** `threshold = float(report.get("threshold", DEFAULT_THRESHOLD))`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `trigger = should_retrain(report)`
> **Type:** Assignment/comparison

### Line  49
> **Code:** `logger.info("Drift score=%.3f threshold=%.3f trigger=%s", score, thres...`
> **Type:** Assignment/comparison

### Line  50
> **Code:** ``
> **Type:** Empty line

### Line  51
> **Code:** `if trigger and not dry_run:`
> **Type:** Conditional statement

### Line  52
> **Code:** `_launch_retraining()`
> **Type:** Function call

### Line  53
> **Code:** `return {`
> **Type:** Returns a value from a function

### Line  54
> **Code:** `"drift_score": score,`
> **Type:** Logical operation

### Line  55
> **Code:** `"threshold": threshold,`
> **Type:** Code statement

### Line  56
> **Code:** `"triggered": trigger,`
> **Type:** Code statement

### Line  57
> **Code:** `"dry_run": dry_run,`
> **Type:** Code statement

### Line  58
> **Code:** `"drifted_features": report.get("drifted_features", []),`
> **Type:** Logical operation

### Line  59
> **Code:** `}`
> **Type:** Code statement

### Line  60
> **Code:** ``
> **Type:** Empty line

### Line  61
> **Code:** ``
> **Type:** Empty line

### Line  62
> **Code:** `def _launch_retraining() -> None:`
> **Type:** Function definition

### Line  63
> **Code:** `train_script = REPO_ROOT / "ml" / "training" / "train.py"`
> **Type:** Assignment/comparison

### Line  64
> **Code:** `evaluate_script = REPO_ROOT / "ml" / "evaluation" / "evaluate.py"`
> **Type:** Assignment/comparison

### Line  65
> **Code:** `cmds = [`
> **Type:** Assignment/comparison

### Line  66
> **Code:** `[sys.executable, str(train_script)],`
> **Type:** Data structure operation

### Line  67
> **Code:** `[sys.executable, str(evaluate_script)],`
> **Type:** Data structure operation

### Line  68
> **Code:** `]`
> **Type:** Code statement

### Line  69
> **Code:** `for cmd in cmds:`
> **Type:** For loop

### Line  70
> **Code:** `logger.info("AUTOMATED_RETRAINING -> %s", " ".join(cmd))`
> **Type:** Arithmetic operation

### Line  71
> **Code:** `subprocess.run(cmd, cwd=REPO_ROOT, check=False)`
> **Type:** Assignment/comparison

### Line  72
> **Code:** `logger.warning("AUTOMATED_RETRAINING_TRIGGERED score=%.3f", read_drift...`
> **Type:** Assignment/comparison

### Line  73
> **Code:** ``
> **Type:** Empty line

### Line  74
> **Code:** ``
> **Type:** Empty line

### Line  75
> **Code:** `def main() -> None:`
> **Type:** Function definition

### Line  76
> **Code:** `logging.basicConfig(level=logging.INFO)`
> **Type:** Assignment/comparison

### Line  77
> **Code:** `parser = argparse.ArgumentParser(description="Drift-based retraining t...`
> **Type:** Assignment/comparison

### Line  78
> **Code:** `parser.add_argument("--dry-run", action="store_true", help="Only repor...`
> **Type:** Assignment/comparison

### Line  79
> **Code:** `args = parser.parse_args()`
> **Type:** Assignment/comparison

### Line  80
> **Code:** `print(json.dumps(trigger_retraining(dry_run=args.dry_run), indent=2))`
> **Type:** Prints output to console

### Line  81
> **Code:** ``
> **Type:** Empty line

### Line  82
> **Code:** ``
> **Type:** Empty line

### Line  83
> **Code:** `if __name__ == "__main__":`
> **Type:** Conditional statement

### Line  84
> **Code:** `main()`
> **Type:** Function call

## Summary
- **Total lines:** 84
- **Code lines:** 63
- **Comments:** 0
- **TODO items:** 3
- **Empty lines:** 18

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: retraining_trigger.py*
---

# mlops-platform-spec-detailed: generate_maintenance_data.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/ml/data/raw/generate_maintenance_data.py`
- **Total lines:** 91
- **File size:** 3096 bytes

## Line Type Summary
- **Code:** 70
- **Comment:** 1
- **Empty:** 17
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `#!/usr/bin/env python3`
> **Type:** Comment: !/usr/bin/env python3

### Line   2
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   3
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   4
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   5
> **Code:** `"""Generate the synthetic predictive maintenance dataset.`
> **Type:** Code statement

### Line   6
> **Code:** ``
> **Type:** Empty line

### Line   7
> **Code:** `Source schema (matches the API contract and ML pipeline):`
> **Type:** Logical operation

### Line   8
> **Code:** `- machine_id: unique identifier (MACH-000000 ...)`
> **Type:** Arithmetic operation

### Line   9
> **Code:** `- equipment_type: pump / motor / compressor / turbine`
> **Type:** Arithmetic operation

### Line  10
> **Code:** `- age_months: equipment age in months (1-300)`
> **Type:** Arithmetic operation

### Line  11
> **Code:** `- operating_hours: total operating hours`
> **Type:** Arithmetic operation

### Line  12
> **Code:** `- maintenance_history: number of past maintenance events (0-100)`
> **Type:** Arithmetic operation

### Line  13
> **Code:** `- sensor_temp / sensor_vibration / sensor_pressure / sensor_humidity`
> **Type:** Arithmetic operation

### Line  14
> **Code:** `- failure_next_30_days: binary target (1 = failure expected within 30 ...`
> **Type:** Assignment/comparison

### Line  15
> **Code:** ``
> **Type:** Empty line

### Line  16
> **Code:** `Deterministic (seeded RNG) so the committed dataset is reproducible.`
> **Type:** Code statement

### Line  17
> **Code:** ``
> **Type:** Empty line

### Line  18
> **Code:** `Output: ml/data/raw/maintenance.csv`
> **Type:** Arithmetic operation

### Line  19
> **Code:** `"""`
> **Type:** Code statement

### Line  20
> **Code:** ``
> **Type:** Empty line

### Line  21
> **Code:** `import os`
> **Type:** Imports a module

### Line  22
> **Code:** ``
> **Type:** Empty line

### Line  23
> **Code:** `import numpy as np`
> **Type:** Imports a module

### Line  24
> **Code:** `import pandas as pd`
> **Type:** Imports a module

### Line  25
> **Code:** ``
> **Type:** Empty line

### Line  26
> **Code:** `OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mai...`
> **Type:** Assignment/comparison

### Line  27
> **Code:** ``
> **Type:** Empty line

### Line  28
> **Code:** `N_ROWS = 40000`
> **Type:** Assignment/comparison

### Line  29
> **Code:** `FAILURE_RATE = 0.20`
> **Type:** Assignment/comparison

### Line  30
> **Code:** `EQUIPMENT_TYPES = ["pump", "motor", "compressor", "turbine"]`
> **Type:** Assignment/comparison

### Line  31
> **Code:** `SEED = 42`
> **Type:** Assignment/comparison

### Line  32
> **Code:** ``
> **Type:** Empty line

### Line  33
> **Code:** `EQUIPMENT_BASE_RISK = {`
> **Type:** Assignment/comparison

### Line  34
> **Code:** `"pump": 0.8,`
> **Type:** Code statement

### Line  35
> **Code:** `"motor": 1.0,`
> **Type:** Logical operation

### Line  36
> **Code:** `"compressor": 1.3,`
> **Type:** Logical operation

### Line  37
> **Code:** `"turbine": 1.6,`
> **Type:** Code statement

### Line  38
> **Code:** `}`
> **Type:** Code statement

### Line  39
> **Code:** ``
> **Type:** Empty line

### Line  40
> **Code:** ``
> **Type:** Empty line

### Line  41
> **Code:** `def generate() -> pd.DataFrame:`
> **Type:** Function definition

### Line  42
> **Code:** `rng = np.random.default_rng(SEED)`
> **Type:** Assignment/comparison

### Line  43
> **Code:** ``
> **Type:** Empty line

### Line  44
> **Code:** `equipment_type = rng.choice(EQUIPMENT_TYPES, size=N_ROWS)`
> **Type:** Assignment/comparison

### Line  45
> **Code:** `age_months = rng.integers(1, 301, size=N_ROWS)`
> **Type:** Assignment/comparison

### Line  46
> **Code:** `operating_hours = np.round(rng.uniform(0, 200000, size=N_ROWS), 1)`
> **Type:** Assignment/comparison

### Line  47
> **Code:** `maintenance_history = rng.integers(0, 101, size=N_ROWS)`
> **Type:** Assignment/comparison

### Line  48
> **Code:** `sensor_temp = np.round(rng.uniform(0, 200, size=N_ROWS), 2)`
> **Type:** Assignment/comparison

### Line  49
> **Code:** `sensor_vibration = np.round(rng.uniform(0, 15, size=N_ROWS), 4)`
> **Type:** Assignment/comparison

### Line  50
> **Code:** `sensor_pressure = np.round(rng.uniform(0, 100, size=N_ROWS), 2)`
> **Type:** Assignment/comparison

### Line  51
> **Code:** `sensor_humidity = np.round(rng.uniform(0, 100, size=N_ROWS), 2)`
> **Type:** Assignment/comparison

### Line  52
> **Code:** ``
> **Type:** Empty line

### Line  53
> **Code:** `risk = (`
> **Type:** Assignment/comparison

### Line  54
> **Code:** `np.array([EQUIPMENT_BASE_RISK[t] for t in equipment_type])`
> **Type:** Logical operation

### Line  55
> **Code:** `+ age_months / 300.0`
> **Type:** Arithmetic operation

### Line  56
> **Code:** `+ operating_hours / 200000.0`
> **Type:** Arithmetic operation

### Line  57
> **Code:** `+ sensor_vibration / 15.0`
> **Type:** Arithmetic operation

### Line  58
> **Code:** `+ (sensor_temp - 100).clip(min=0) / 100.0`
> **Type:** Assignment/comparison

### Line  59
> **Code:** `+ (sensor_pressure - 60).clip(min=0) / 40.0`
> **Type:** Assignment/comparison

### Line  60
> **Code:** `- maintenance_history / 100.0`
> **Type:** Arithmetic operation

### Line  61
> **Code:** `)`
> **Type:** Code statement

### Line  62
> **Code:** `risk = risk / risk.mean() * FAILURE_RATE`
> **Type:** Assignment/comparison

### Line  63
> **Code:** `failure_next_30_days = (rng.random(N_ROWS) < risk).astype(int)`
> **Type:** Assignment/comparison

### Line  64
> **Code:** ``
> **Type:** Empty line

### Line  65
> **Code:** `return pd.DataFrame(`
> **Type:** Returns a value from a function

### Line  66
> **Code:** `{`
> **Type:** Data structure operation

### Line  67
> **Code:** `"machine_id": [f"MACH-{i:06d}" for i in range(N_ROWS)],`
> **Type:** Arithmetic operation

### Line  68
> **Code:** `"equipment_type": equipment_type,`
> **Type:** Code statement

### Line  69
> **Code:** `"age_months": age_months,`
> **Type:** Code statement

### Line  70
> **Code:** `"operating_hours": operating_hours,`
> **Type:** Code statement

### Line  71
> **Code:** `"maintenance_history": maintenance_history,`
> **Type:** Logical operation

### Line  72
> **Code:** `"sensor_temp": sensor_temp,`
> **Type:** Logical operation

### Line  73
> **Code:** `"sensor_vibration": sensor_vibration,`
> **Type:** Logical operation

### Line  74
> **Code:** `"sensor_pressure": sensor_pressure,`
> **Type:** Logical operation

### Line  75
> **Code:** `"sensor_humidity": sensor_humidity,`
> **Type:** Logical operation

### Line  76
> **Code:** `"failure_next_30_days": failure_next_30_days,`
> **Type:** Code statement

### Line  77
> **Code:** `}`
> **Type:** Code statement

### Line  78
> **Code:** `)`
> **Type:** Code statement

### Line  79
> **Code:** ``
> **Type:** Empty line

### Line  80
> **Code:** ``
> **Type:** Empty line

### Line  81
> **Code:** `def main() -> None:`
> **Type:** Function definition

### Line  82
> **Code:** `df = generate()`
> **Type:** Assignment/comparison

### Line  83
> **Code:** `df.to_csv(OUTPUT, index=False)`
> **Type:** Assignment/comparison

### Line  84
> **Code:** `rate = df["failure_next_30_days"].mean() * 100`
> **Type:** Assignment/comparison

### Line  85
> **Code:** `print(f"Wrote {len(df):,} rows -> {OUTPUT}")`
> **Type:** Prints output to console

### Line  86
> **Code:** `print(f"  failures={df['failure_next_30_days'].sum():,} ({rate:.2f}%)"...`
> **Type:** Prints output to console

### Line  87
> **Code:** `print(f"  equipment types: {dict(df['equipment_type'].value_counts())}...`
> **Type:** Prints output to console

### Line  88
> **Code:** ``
> **Type:** Empty line

### Line  89
> **Code:** ``
> **Type:** Empty line

### Line  90
> **Code:** `if __name__ == "__main__":`
> **Type:** Conditional statement

### Line  91
> **Code:** `main()`
> **Type:** Function call

## Summary
- **Total lines:** 91
- **Code lines:** 70
- **Comments:** 1
- **TODO items:** 3
- **Empty lines:** 17

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: generate_maintenance_data.py*
---

# mlops-platform-spec-detailed: generate_telco_churn.py

## File Information
- **File path:** `/home/gadour/Desktop/new_project/other/mlops-platform-spec-detailed/ml/data/raw/generate_telco_churn.py`
- **Total lines:** 145
- **File size:** 5311 bytes

## Line Type Summary
- **Code:** 110
- **Comment:** 5
- **Empty:** 27
- **TODO:** 3

## Detailed Line Explanations

### Line   1
> **Code:** `#!/usr/bin/env python3`
> **Type:** Comment: !/usr/bin/env python3

### Line   2
> **Code:** `# TODO: medium - Add type hints where missing`
> **Type:** TODO: medium - Add type hints where missing

### Line   3
> **Code:** `# TODO: low - Add comprehensive docstring`
> **Type:** TODO: low - Add comprehensive docstring

### Line   4
> **Code:** `# TODO: low - Add error handling for edge cases`
> **Type:** TODO: low - Add error handling for edge cases

### Line   5
> **Code:** `"""Generate a realistic synthetic Telco Customer Churn dataset.`
> **Type:** Code statement

### Line   6
> **Code:** ``
> **Type:** Empty line

### Line   7
> **Code:** `Produces ~7,000 rows with the standard Telco churn schema (numeric + c...`
> **Type:** Arithmetic operation

### Line   8
> **Code:** `features matching the classic public dataset) plus a derived churn lab...`
> **Type:** Code statement

### Line   9
> **Code:** ``
> **Type:** Empty line

### Line  10
> **Code:** `Output: ml/data/raw/telco_churn.csv`
> **Type:** Arithmetic operation

### Line  11
> **Code:** `Deterministic (fixed seed) so training runs are reproducible.`
> **Type:** Code statement

### Line  12
> **Code:** `"""`
> **Type:** Code statement

### Line  13
> **Code:** ``
> **Type:** Empty line

### Line  14
> **Code:** `from __future__ import annotations`
> **Type:** Imports specific names from a module

### Line  15
> **Code:** ``
> **Type:** Empty line

### Line  16
> **Code:** `import argparse`
> **Type:** Imports a module

### Line  17
> **Code:** `import os`
> **Type:** Imports a module

### Line  18
> **Code:** ``
> **Type:** Empty line

### Line  19
> **Code:** `import numpy as np`
> **Type:** Imports a module

### Line  20
> **Code:** `import pandas as pd`
> **Type:** Imports a module

### Line  21
> **Code:** ``
> **Type:** Empty line

### Line  22
> **Code:** `RAW_DIR = os.path.dirname(os.path.abspath(__file__))`
> **Type:** Assignment/comparison

### Line  23
> **Code:** `DEFAULT_OUTPUT = os.path.join(RAW_DIR, "telco_churn.csv")`
> **Type:** Assignment/comparison

### Line  24
> **Code:** ``
> **Type:** Empty line

### Line  25
> **Code:** `RNG = np.random.default_rng(42)`
> **Type:** Assignment/comparison

### Line  26
> **Code:** ``
> **Type:** Empty line

### Line  27
> **Code:** `N_DEFAULTS = 7000`
> **Type:** Assignment/comparison

### Line  28
> **Code:** ``
> **Type:** Empty line

### Line  29
> **Code:** `CONTRACT_TYPES = ["month-to-month", "one year", "two year"]`
> **Type:** Assignment/comparison

### Line  30
> **Code:** `PAYMENT_METHODS = [`
> **Type:** Assignment/comparison

### Line  31
> **Code:** `"electronic_check",`
> **Type:** Code statement

### Line  32
> **Code:** `"mailed_check",`
> **Type:** Code statement

### Line  33
> **Code:** `"bank_transfer",`
> **Type:** Code statement

### Line  34
> **Code:** `"credit_card",`
> **Type:** Code statement

### Line  35
> **Code:** `]`
> **Type:** Code statement

### Line  36
> **Code:** `INTERNET_SERVICES = ["DSL", "Fiber optic", "No"]`
> **Type:** Assignment/comparison

### Line  37
> **Code:** `ADDON_SERVICES = ["OnlineSecurity", "OnlineBackup", "DeviceProtection"...`
> **Type:** Assignment/comparison

### Line  38
> **Code:** ``
> **Type:** Empty line

### Line  39
> **Code:** `GENDER = ["Male", "Female"]`
> **Type:** Assignment/comparison

### Line  40
> **Code:** `PARTNER = ["Yes", "No"]`
> **Type:** Assignment/comparison

### Line  41
> **Code:** `DEPENDENTS = ["Yes", "No"]`
> **Type:** Assignment/comparison

### Line  42
> **Code:** `PHONE_SERVICE = ["Yes", "No"]`
> **Type:** Assignment/comparison

### Line  43
> **Code:** `MULTIPLE_LINES = ["Yes", "No", "No phone service"]`
> **Type:** Assignment/comparison

### Line  44
> **Code:** `YES_NO_NO_PHONE = ["Yes", "No", "No internet service"]`
> **Type:** Assignment/comparison

### Line  45
> **Code:** ``
> **Type:** Empty line

### Line  46
> **Code:** ``
> **Type:** Empty line

### Line  47
> **Code:** `def _weighted_choice(options: list[str], probs: list[float]) -> str:`
> **Type:** Function definition

### Line  48
> **Code:** `return str(RNG.choice(options, p=probs))`
> **Type:** Returns a value from a function

### Line  49
> **Code:** ``
> **Type:** Empty line

### Line  50
> **Code:** ``
> **Type:** Empty line

### Line  51
> **Code:** `def generate(n_rows: int = N_DEFAULTS) -> pd.DataFrame:`
> **Type:** Function definition

### Line  52
> **Code:** `rows: list[dict] = []`
> **Type:** Assignment/comparison

### Line  53
> **Code:** `for i in range(n_rows):`
> **Type:** For loop

### Line  54
> **Code:** `tenure = int(RNG.integers(0, 73))`
> **Type:** Assignment/comparison

### Line  55
> **Code:** `contract = _weighted_choice(CONTRACT_TYPES, [0.55, 0.24, 0.21])`
> **Type:** Assignment/comparison

### Line  56
> **Code:** `internet = _weighted_choice(INTERNET_SERVICES, [0.45, 0.44, 0.11])`
> **Type:** Assignment/comparison

### Line  57
> **Code:** `monthly = 0.0`
> **Type:** Assignment/comparison

### Line  58
> **Code:** ``
> **Type:** Empty line

### Line  59
> **Code:** `if internet == "Fiber optic":`
> **Type:** Conditional statement

### Line  60
> **Code:** `monthly += RNG.uniform(50.0, 105.0)`
> **Type:** Assignment/comparison

### Line  61
> **Code:** `elif internet == "DSL":`
> **Type:** Else-if branch

### Line  62
> **Code:** `monthly += RNG.uniform(20.0, 55.0)`
> **Type:** Assignment/comparison

### Line  63
> **Code:** ``
> **Type:** Empty line

### Line  64
> **Code:** `# Contract type shapes monthly charges.`
> **Type:** Comment: Contract type shapes monthly charges.

### Line  65
> **Code:** `if contract == "two year":`
> **Type:** Conditional statement

### Line  66
> **Code:** `monthly += RNG.uniform(10.0, 20.0)`
> **Type:** Assignment/comparison

### Line  67
> **Code:** `elif contract == "one year":`
> **Type:** Else-if branch

### Line  68
> **Code:** `monthly += RNG.uniform(5.0, 12.0)`
> **Type:** Assignment/comparison

### Line  69
> **Code:** `else:`
> **Type:** Else block

### Line  70
> **Code:** `monthly += RNG.uniform(0.0, 8.0)`
> **Type:** Assignment/comparison

### Line  71
> **Code:** ``
> **Type:** Empty line

### Line  72
> **Code:** `addons = RNG.choice(ADDON_SERVICES, size=int(RNG.integers(0, 5)), repl...`
> **Type:** Assignment/comparison

### Line  73
> **Code:** `for addon in addons:`
> **Type:** For loop

### Line  74
> **Code:** `monthly += 7.0 if addon != "StreamingTV" else 10.0`
> **Type:** Assignment/comparison

### Line  75
> **Code:** ``
> **Type:** Empty line

### Line  76
> **Code:** `if _weighted_choice(["Yes", "No"], [0.9, 0.1]) == "Yes":`
> **Type:** Conditional statement

### Line  77
> **Code:** `phone_service = "Yes"`
> **Type:** Assignment/comparison

### Line  78
> **Code:** `multiple_lines = _weighted_choice(["Yes", "No"], [0.42, 0.58])`
> **Type:** Assignment/comparison

### Line  79
> **Code:** `else:`
> **Type:** Else block

### Line  80
> **Code:** `phone_service = "No"`
> **Type:** Assignment/comparison

### Line  81
> **Code:** `multiple_lines = "No phone service"`
> **Type:** Assignment/comparison

### Line  82
> **Code:** ``
> **Type:** Empty line

### Line  83
> **Code:** `payment = _weighted_choice(PAYMENT_METHODS, [0.34, 0.23, 0.22, 0.21])`
> **Type:** Assignment/comparison

### Line  84
> **Code:** ``
> **Type:** Empty line

### Line  85
> **Code:** `total = monthly * (tenure if tenure > 0 else 1)`
> **Type:** Assignment/comparison

### Line  86
> **Code:** `# Churn probability grows with month-to-month + electronic check,`
> **Type:** Comment: Churn probability grows with month-to-month + electronic check,

### Line  87
> **Code:** `# shrinks with tenure.`
> **Type:** Comment: shrinks with tenure.

### Line  88
> **Code:** `p_churn = (`
> **Type:** Assignment/comparison

### Line  89
> **Code:** `0.08`
> **Type:** Code statement

### Line  90
> **Code:** `+ 0.35 * (contract == "month-to-month")`
> **Type:** Assignment/comparison

### Line  91
> **Code:** `+ 0.18 * (payment == "electronic_check")`
> **Type:** Assignment/comparison

### Line  92
> **Code:** `+ 0.15 * (internet == "Fiber optic")`
> **Type:** Assignment/comparison

### Line  93
> **Code:** `- 0.012 * tenure`
> **Type:** Arithmetic operation

### Line  94
> **Code:** `)`
> **Type:** Code statement

### Line  95
> **Code:** `p_churn = float(np.clip(p_churn, 0.01, 0.95))`
> **Type:** Assignment/comparison

### Line  96
> **Code:** `churn = "Yes" if RNG.random() < p_churn else "No"`
> **Type:** Assignment/comparison

### Line  97
> **Code:** ``
> **Type:** Empty line

### Line  98
> **Code:** `rows.append(`
> **Type:** Code statement

### Line  99
> **Code:** `{`
> **Type:** Data structure operation

### Line 100
> **Code:** `"customer_id": f"CUST-{i:05d}",`
> **Type:** Arithmetic operation

### Line 101
> **Code:** `"gender": _weighted_choice(GENDER, [0.5, 0.5]),`
> **Type:** Data structure operation

### Line 102
> **Code:** `"senior_citizen": int(RNG.integers(0, 2)),`
> **Type:** Logical operation

### Line 103
> **Code:** `"partner": _weighted_choice(PARTNER, [0.48, 0.52]),`
> **Type:** Data structure operation

### Line 104
> **Code:** `"dependents": _weighted_choice(DEPENDENTS, [0.3, 0.7]),`
> **Type:** Data structure operation

### Line 105
> **Code:** `"tenure": tenure,`
> **Type:** Code statement

### Line 106
> **Code:** `"phone_service": phone_service,`
> **Type:** Code statement

### Line 107
> **Code:** `"multiple_lines": multiple_lines,`
> **Type:** Code statement

### Line 108
> **Code:** `"internet_service": internet,`
> **Type:** Code statement

### Line 109
> **Code:** `"online_security": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]),`
> **Type:** Data structure operation

### Line 110
> **Code:** `"online_backup": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]),`
> **Type:** Data structure operation

### Line 111
> **Code:** `"device_protection": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]...`
> **Type:** Data structure operation

### Line 112
> **Code:** `"tech_support": _weighted_choice(YES_NO_NO_PHONE, [0.25, 0.45, 0.3]),`
> **Type:** Logical operation

### Line 113
> **Code:** `"streaming_tv": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]),`
> **Type:** Data structure operation

### Line 114
> **Code:** `"streaming_movies": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3])...`
> **Type:** Data structure operation

### Line 115
> **Code:** `"contract": contract,`
> **Type:** Code statement

### Line 116
> **Code:** `"paperless_billing": _weighted_choice(["Yes", "No"], [0.6, 0.4]),`
> **Type:** Data structure operation

### Line 117
> **Code:** `"payment_method": payment,`
> **Type:** Code statement

### Line 118
> **Code:** `"monthly_charges": round(monthly, 2),`
> **Type:** Code statement

### Line 119
> **Code:** `"total_charges": round(total, 2),`
> **Type:** Code statement

### Line 120
> **Code:** `"churn": churn,`
> **Type:** Code statement

### Line 121
> **Code:** `}`
> **Type:** Code statement

### Line 122
> **Code:** `)`
> **Type:** Code statement

### Line 123
> **Code:** ``
> **Type:** Empty line

### Line 124
> **Code:** `df = pd.DataFrame(rows)`
> **Type:** Assignment/comparison

### Line 125
> **Code:** `# Guarantee realistic ~7000 rows by adjusting to target when asked.`
> **Type:** Comment: Guarantee realistic ~7000 rows by adjusting to target when asked.

### Line 126
> **Code:** `return df`
> **Type:** Returns a value from a function

### Line 127
> **Code:** ``
> **Type:** Empty line

### Line 128
> **Code:** ``
> **Type:** Empty line

### Line 129
> **Code:** `def main() -> None:`
> **Type:** Function definition

### Line 130
> **Code:** `parser = argparse.ArgumentParser(description="Generate synthetic Telco...`
> **Type:** Assignment/comparison

### Line 131
> **Code:** `parser.add_argument("--rows", type=int, default=N_DEFAULTS, help="Numb...`
> **Type:** Assignment/comparison

### Line 132
> **Code:** `parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help...`
> **Type:** Assignment/comparison

### Line 133
> **Code:** `args = parser.parse_args()`
> **Type:** Assignment/comparison

### Line 134
> **Code:** ``
> **Type:** Empty line

### Line 135
> **Code:** `df = generate(args.rows)`
> **Type:** Assignment/comparison

### Line 136
> **Code:** `df.to_csv(args.output, index=False)`
> **Type:** Assignment/comparison

### Line 137
> **Code:** `n_churn = int((df["churn"] == "Yes").sum())`
> **Type:** Assignment/comparison

### Line 138
> **Code:** `print(`
> **Type:** Prints output to console

### Line 139
> **Code:** `f"Wrote {len(df):,} rows -> {args.output}\n"`
> **Type:** Arithmetic operation

### Line 140
> **Code:** `f"  churn=Yes: {n_churn:,} ({n_churn / len(df):.1%})"`
> **Type:** Assignment/comparison

### Line 141
> **Code:** `)`
> **Type:** Code statement

### Line 142
> **Code:** ``
> **Type:** Empty line

### Line 143
> **Code:** ``
> **Type:** Empty line

### Line 144
> **Code:** `if __name__ == "__main__":`
> **Type:** Conditional statement

### Line 145
> **Code:** `main()`
> **Type:** Function call

## Summary
- **Total lines:** 145
- **Code lines:** 110
- **Comments:** 5
- **TODO items:** 3
- **Empty lines:** 27

---
*Documentation generated for: mlops-platform-spec-detailed*
*File: generate_telco_churn.py*
---

