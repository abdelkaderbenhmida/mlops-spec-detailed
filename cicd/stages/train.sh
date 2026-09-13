#!/usr/bin/env bash
# CI/CD stage: train the model, register it in MLflow, and gate on evaluation.
#
# Spec section 9 stage 2: the pipeline only proceeds if ml/evaluation/evaluate.py
# confirms the new model beats (or ties within tolerance) the current Production
# model. evaluate.py exits non-zero when F1 regresses beyond
# evaluation.max_f1_regression in ml/training/config.yml, which fails this stage
# before the promotion approval gate is offered.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-http://localhost:5000}"

echo "== training and registering model =="
python3 ml/training/train.py

echo "== evaluating new model against current Production =="
python3 ml/evaluation/evaluate.py

echo "Train stage complete."
