#!/usr/bin/env bash
# CI/CD stage: run the API test suite.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [ -d ".venv" ]; then
    . .venv/bin/activate
fi

echo "== running API tests =="
python3 -m pytest api/tests -q
echo "Test stage complete."
