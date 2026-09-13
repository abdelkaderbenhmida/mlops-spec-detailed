#!/usr/bin/env bash
# Provision infrastructure + generate inventory + configure everything (steps 1-3 of the deployment workflow).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="${ROOT_DIR}/terraform"
ANSIBLE_DIR="${ROOT_DIR}/ansible"

log() { printf '\033[1;34m[bootstrap]\033[0m %s\n' "$*"; }

log "Step 1/3: provisioning infrastructure with Terraform"
cd "${TF_DIR}"
terraform init -input=false
terraform apply -auto-approve

log "Step 2/3: generating Ansible inventory"
python3 "${ROOT_DIR}/scripts/generate-inventory.py" > "${ANSIBLE_DIR}/inventory/hosts.ini"
cat "${ANSIBLE_DIR}/inventory/hosts.ini"

log "Step 3/3: configuring servers with Ansible"
cd "${ANSIBLE_DIR}"
ansible-playbook -i inventory/hosts.ini site.yml

log "Bootstrap complete."
echo
log "Next steps:"
log "  ./scripts/train-and-register.sh          # train + register the first model"
log "  kubectl apply -f ${ROOT_DIR}/kubernetes/ # deploy the FastAPI serving layer"
log "  ./scripts/smoke-test.sh                  # verify /predict"
