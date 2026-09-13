#!/usr/bin/env bash
# CI/CD stage: build the FastAPI Docker image.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

IMAGE_NAME="${IMAGE_NAME:-mlops-fastapi}"
BUILD_NUMBER="${BUILD_NUMBER:-local}"
TAG="${IMAGE_NAME}:${BUILD_NUMBER}"

echo "== building ${TAG} =="
docker build -t "${TAG}" -f docker/fastapi/Dockerfile docker/fastapi

echo "${TAG}" > /tmp/mlops-image-tag.txt
echo "Build stage complete: ${TAG}"
