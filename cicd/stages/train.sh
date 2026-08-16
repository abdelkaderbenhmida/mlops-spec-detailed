#!/usr/bin/env bash
# CI/CD stage: train the model and register it in MLflow.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-http://10.0.2.30:5000}" \
    python3 ml/training/train.py

echo "Train stage complete."
