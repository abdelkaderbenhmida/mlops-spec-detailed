# Deployment Guide

Full bootstrap sequence from bare-metal plant hardware to a serving `/predict` endpoint —
with no internet connectivity at any point — plus how to trigger a retrain through CI/CD
and how updates enter the plant.

## Prerequisites

On the machine that will run Terraform and Ansible (VM01, or the plant jump host for the
very first run):

- Terraform >= 1.5 with the libvirt provider (from the VM12 provider mirror)
- Ansible >= 2.15
- Python 3.11 with `pyyaml`
- `kubectl`
- Hypervisor credentials for Proxmox/bare KVM (the plant's virtualization platform — there
  are no cloud credentials in this project)
- An SSH keypair whose public key is referenced in `terraform.tfvars`
- The first **signed update bundle** on approved removable media (see §"Updating the
  platform" below) — nothing can be installed until the mirror exists

## Secrets

Nothing sensitive is committed. Before the first apply:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# fill in: hypervisor_endpoint, machine_types, ssh_public_key, admin_cidr, gpu_passthrough
```

Database and MLflow credentials are supplied to Ansible as variables (use
`ansible-vault encrypt` on `ansible/inventory/group_vars/all.yml`, or pass `-e` at run time)
and reach the API through `kubernetes/inference/secret.yml`, which holds base64 placeholders
that must be replaced before `kubectl apply`. The API reads `DB_USER`, `DB_PASSWORD`,
`DB_HOST`, `DB_PORT` and `DB_NAME` from the environment (`api/app/db.py`); it never contains
literal credentials.

## Full bootstrap

```bash
# 0. OT security approval first
#     Data-flow diagram signed off by the OT Security Manager; diode vs. egress-only
#     firewall decision made. This is a phase-0 gate, not a formality.

# 1. Provision infrastructure (12 VMs on the plant hypervisor)
cd terraform
terraform init
terraform apply -auto-approve

# 2. Import the first signed update bundle onto VM12
#     Signature is verified; the bundle is refused on mismatch, no exceptions.
cd ../scripts
./import-update-bundle.sh anvil-update-2026-08.tar.gz

# 3. Generate the Ansible inventory from the Terraform IP plan
python3 generate-inventory.py > ../ansible/inventory/hosts.ini

# 4. Configure every VM (mirror first, then K8s, TimescaleDB, MLflow, ingest, Jenkins, monitoring)
cd ../ansible
ansible-playbook -i inventory/hosts.ini site.yml

# 5. Verify MLflow and TimescaleDB are up
curl http://10.20.2.30:5000/health
psql -h 10.20.2.40 -U mlflow -d mlflow -c '\dt'

# 6. Verify the OPC-UA ingestion path is live
curl http://10.20.2.31:8000/ingest/status   # tag rate, buffer depth, unmapped tags

# 7. Train and register the first model (shadow mode — see main spec §14 phase 15)
cd ..
./scripts/train-and-register.sh          # → Staging
./scripts/train-and-register.sh --promote  # → Production (first model, manual gate)

# 8. Deploy the serving and alerting layers
kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/inference/
kubectl apply -f kubernetes/alerting/
kubectl apply -f kubernetes/hpa.yml

# 9. Smoke test
./scripts/smoke-test.sh

# 10. Verify monitoring
curl http://10.20.2.50:9090/-/healthy
curl http://10.20.2.51:3000/api/health
```

`scripts/bootstrap.sh` wraps steps 1-5. The `Makefile` mirrors every step:
`make provision`, `make import-bundle`, `make inventory`, `make configure`, `make bootstrap`,
`make train`, `make evaluate`, `make promote`, `make test`, `make build-image`,
`make deploy-k8s`, `make smoke`, `make validate`.

## Verifying each layer

| Layer | Check | Expected |
|---|---|---|
| Kubernetes | `kubectl get nodes` | 3 nodes `Ready` |
| Namespace | `kubectl get all -n mlops` | `deployment/inference`, `deployment/alerting`, services, HPA |
| MLflow | open `http://10.20.2.30:5000` | experiment `anvil-health` with runs |
| Registry | `mlflow models list` / Registry UI | `anvil-health` with a `Production` version |
| Ingestion | `curl http://10.20.2.31:8000/ingest/status` | non-zero tag rate, buffer draining, zero unmapped tags |
| TimescaleDB | `psql -h 10.20.2.40 -U mlops_app -d mlops -c "SELECT count(*) FROM sensor_telemetry;"` | rows increasing |
| API | `curl http://api.mlops.local/health` | `{"status":"healthy","model_loaded":true,...}` |
| Model in use | `curl http://api.mlops.local/model-info` | the version you promoted |
| Metrics | `curl http://api.mlops.local/metrics` | Prometheus text exposition |
| Prometheus | `http://10.20.2.50:9090/targets` | all targets `UP` |
| Grafana | `http://10.20.2.51:3000` | platform dashboards + operator line dashboard with live data |

## Triggering a retrain via CI/CD

The Jenkins pipeline (`cicd/Jenkinsfile`, running on VM02, triggered by Gitea webhooks —
fully offline, no GitHub) has these stages:

1. **Checkout** — on push to `main`, or on the retraining schedule.
2. **Train** (`cicd/stages/train.sh`) — runs `ml/training/train.py` on VM11 and then
   `ml/evaluation/evaluate.py`. Evaluation exits non-zero if alert precision regresses
   beyond the tolerance in `ml/training/config.yml` against the current `Production`
   model, which fails the build before anything is promoted.
3. **Register & Promote** — a Jenkins `input` step asks for the MLflow model version and
   waits for a human approval, then transitions that version to `Production`.
4. **Test** (`cicd/stages/test.sh`) — `pytest api/tests`.
5. **Build** (`cicd/stages/build.sh`) — builds and tags the inference image (code only),
   pushed to Harbor on VM12. No public registry exists.
6. **Deploy** (`cicd/stages/deploy.sh`) — `kubectl set image` +
   `kubectl rollout restart deployment/inference -n mlops`, so every pod re-pulls the newly
   promoted `Production` model on startup.
7. **Smoke test** (`cicd/stages/smoke.sh`) — POSTs a known sensor window to `/predict` and
   checks for a 200 with a health score in `[0, 1]`.

To retrain manually without touching the pipeline:

```bash
make train      # train + register + Staging
make evaluate   # gate: exits 2 if precision regressed too far
make promote    # manual gate: Staging → Production
kubectl rollout restart deployment/inference -n mlops
```

Model updates never require a package or image update: they are artifacts in the local
MLflow registry. That separation is what keeps the system improvable inside an air gap.

## Updating the platform

There is no internet inside the plant. Every dependency enters via a **signed update
bundle** on approved removable media:

1. On an internet-connected staging machine outside the plant: pull pinned versions, run
   Trivy vulnerability scanning (the only patching gate that exists offline), export
   `anvil-update-<yyyymm>.tar.gz` + detached signature.
2. Physical transfer per the plant's media policy — typically including a scanning kiosk.
   Budget days for this, not minutes.
3. Inside the plant: `scripts/import-update-bundle.sh` verifies the signature (refuses on
   mismatch), imports to VM12, deploys to a staging namespace first, then promotes in an
   approved maintenance window.

Cadence is monthly at best, quarterly in practice. Every version is pinned; there are no
`latest` tags; VM12 keeps N-2 versions of every image so rollback never requires a physical
transfer during an incident. The delta between installed and current upstream versions is
tracked and reported — the security team will ask.

## Rolling back

Rollback is a registry operation, not an image operation — the image contains no model:

```bash
# Point Production back at the previous version (kept on VM12 / local registry)
python3 - <<'EOF'
from mlflow.tracking import MlflowClient
c = MlflowClient()
c.transition_model_version_stage("anvil-health", <previous_version>, "Production")
EOF

kubectl rollout restart deployment/inference -n mlops
```

To roll back a *code* change instead, use `kubectl rollout undo deployment/inference -n mlops`
and redeploy the previous image from the VM12 mirror (N-2 retention guarantees it is there).

## Backups

- Nightly TimescaleDB backups to the plant NAS; weekly to removable media held off-site.
- **MLflow artifacts and the model registry are backed up with the same rigour as the
  database** — losing the registry means losing the ability to reproduce the model currently
  making maintenance decisions.
- Restore is tested quarterly. The full-rebuild runbook (bare metal to running platform)
  is executed by plant IT without vendor assistance — assume the vendor cannot get on site
  for 72 hours.

## Tearing down

```bash
make clean               # local artifacts only
cd terraform && terraform destroy
```
