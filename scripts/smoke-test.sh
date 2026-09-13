#!/usr/bin/env bash
# Smoke test: POST a known sample payload to /predict and verify a sane response.
set -euo pipefail

BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Matches api/app/schemas.py::PredictRequest (rotating-equipment sensor window).
payload='{
  "equipment_type": "pump",
  "age_months": 60,
  "operating_hours": 20000.0,
  "maintenance_history": 5,
  "sensor_temp": 70.0,
  "sensor_vibration": 1.0,
  "sensor_pressure": 35.0,
  "sensor_humidity": 50.0
}'

echo "== health =="
curl -fsS "${BASE_URL}/health" || { echo "FAIL: /health unreachable at ${BASE_URL}" >&2; exit 1; }
echo
echo "== predict =="
RESP="$(curl -fsS -X POST "${BASE_URL}/predict" -H 'Content-Type: application/json' -d "${payload}")" || {
    echo "FAIL: /predict returned an error" >&2; exit 1;
}
echo "${RESP}"

python3 - "${RESP}" <<'EOF'
import json
import sys

resp = json.loads(sys.argv[1])
for key in ("prediction", "probability", "risk_level", "model_version", "model_stage"):
    assert key in resp, f"missing '{key}' in {resp}"
assert resp["prediction"] in ("failure", "no_failure"), f"unexpected prediction: {resp}"
assert 0.0 <= float(resp["probability"]) <= 1.0, f"probability out of range: {resp}"
print("OK: /predict returned", resp["prediction"], "with probability", resp["probability"])
EOF

echo "== model-info =="
curl -fsS "${BASE_URL}/model-info" || echo "(no /model-info endpoint; skipped)"
echo
echo "Smoke test passed."
