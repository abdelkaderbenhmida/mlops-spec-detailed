#!/usr/bin/env bash
# Train a model, register it in MLflow, and promote to Staging (or Production with --promote).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
MLFLOW_URI="${MLFLOW_TRACKING_URI:-http://localhost:5000}"
MODEL_NAME="${MODEL_NAME:-maintenance-model}"
PROMOTE=0

usage() {
    echo "Usage: $0 [--promote]" >&2
    echo "  --promote   transition the new model from Staging to Production (manual approval gate)" >&2
    exit 1
}

for arg in "$@"; do
    case "$arg" in
        --promote) PROMOTE=1 ;;
        -h|--help) usage ;;
        *) echo "Unknown argument: $arg" >&2; usage ;;
    esac
done

export MLFLOW_TRACKING_URI="${MLFLOW_URI}"

echo "== training and registering model '${MODEL_NAME}' =="
"${PYTHON}" "${ROOT_DIR}/ml/training/train.py"

NEW_VERSION=$(
    "${PYTHON}" - "${MODEL_NAME}" <<'EOF'
import json
import sys
import mlflow
from mlflow.tracking import MlflowClient

model_name = sys.argv[1]
client = MlflowClient()
versions = client.search_model_versions(f"name='{model_name}'")
if not versions:
    print("0")
    sys.exit(1)
print(max(int(v.version) for v in versions))
EOF
)
echo "registered model version: ${NEW_VERSION}"

if [ "${PROMOTE}" -eq 1 ]; then
    echo "== promoting version ${NEW_VERSION} to Production (manual approval gate) =="
    "${PYTHON}" - "${MODEL_NAME}" "${NEW_VERSION}" <<'EOF'
import sys
import mlflow
from mlflow.tracking import MlflowClient

model_name, version = sys.argv[1], int(sys.argv[2])
client = MlflowClient()
client.transition_model_version_stage(model_name, version, "Production")
client.update_model_version(model_name, version, description="Promoted via train-and-register.sh --promote")
print(f"promoted {model_name} v{version} -> Production")
EOF
else
    echo "== transitioning version ${NEW_VERSION} to Staging =="
    "${PYTHON}" - "${MODEL_NAME}" "${NEW_VERSION}" <<'EOF'
import sys
from mlflow.tracking import MlflowClient

model_name, version = sys.argv[1], int(sys.argv[2])
client = MlflowClient()
client.transition_model_version_stage(model_name, version, "Staging")
print(f"transitioned {model_name} v{version} -> Staging")
EOF
fi

echo "== done =="
