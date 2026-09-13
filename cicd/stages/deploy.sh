#!/usr/bin/env bash
# CI/CD stage: deploy the FastAPI image to Kubernetes and force reload of the Production model.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

IMAGE_NAME="${IMAGE_NAME:-mlops-fastapi}"
BUILD_NUMBER="${BUILD_NUMBER:-local}"
K8S_NS="${K8S_NS:-mlops}"

echo "== applying Kubernetes manifests =="
kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/fastapi/
kubectl apply -f kubernetes/hpa.yml

echo "== rolling restart so pods reload the latest Production model =="
kubectl rollout restart deployment/fastapi -n "${K8S_NS}"
kubectl rollout status deployment/fastapi -n "${K8S_NS}" --timeout=180s

echo "Deploy stage complete."
