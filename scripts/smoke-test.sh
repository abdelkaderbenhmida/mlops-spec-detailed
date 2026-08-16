#!/usr/bin/env bash
# Smoke test: POST a known sample payload to /predict and verify a sane response.
set -euo pipefail

BASE_URL="${API_BASE_URL:-http://localhost:8000}"

payload='{
  "tenure_months": 12,
  "monthly_charges": 70.5,
  "total_charges": 786.0,
  "contract_type": "month-to-month",
  "payment_method": "electronic_check"
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
assert "prediction" in resp, f"missing 'prediction' in {resp}"
assert "probability" in resp, f"missing 'probability' in {resp}"
assert 0.0 <= float(resp["probability"]) <= 1.0, f"probability out of range: {resp}"
print("OK: /predict returned", resp["prediction"], "with probability", resp["probability"])
EOF

echo "== model-info =="
curl -fsS "${BASE_URL}/model-info" || echo "(no /model-info endpoint; skipped)"
echo
echo "Smoke test passed."
