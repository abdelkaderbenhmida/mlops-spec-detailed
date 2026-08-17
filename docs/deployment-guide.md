# Deployment Guide

Full bootstrap sequence from an empty cloud account to a serving `/predict` endpoint, plus
how to trigger a retrain through CI/CD.

## Prerequisites

On the machine that will run Terraform and Ansible (VM01, or your workstation for the very
first run):

- Terraform >= 1.5
- Ansible >= 2.15
- Python 3.11 with `pyyaml`
- `kubectl`
- Cloud provider credentials with permission to create a VPC, firewall rules and 12 VMs
- An SSH keypair whose public key is referenced in `terraform.tfvars`

## Secrets

Nothing sensitive is committed. Before the first apply:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# fill in: project_id, region, zone, ssh_public_key, admin_cidr
```

Database and MLflow credentials are supplied to Ansible as variables (use
`ansible-vault encrypt` on `ansible/inventory/group_vars/all.yml`, or pass `-e` at run time)
and reach the API through `kubernetes/fastapi/secret.yml`, which holds base64 placeholders
that must be replaced before `kubectl apply`. The API reads `DB_USER`, `DB_PASSWORD`,
`DB_HOST`, `DB_PORT` and `DB_NAME` from the environment (`api/app/db.py`); it never contains
literal credentials.

## Full bootstrap

```bash
# 1. Provision infrastructure (VPC, subnets, security groups, 12 VMs)
cd terraform
terraform init
terraform apply -auto-approve

# 2. Generate the Ansible inventory from the Terraform IP plan
cd ../scripts
python3 generate-inventory.py > ../ansible/inventory/hosts.ini

# 3. Configure every VM (K8s cluster, MLflow, Postgres, Jenkins, monitoring)
cd ../ansible
ansible-playbook -i inventory/hosts.ini site.yml

# 4. Verify MLflow and PostgreSQL are up
curl http://10.0.2.30:5000/health
psql -h 10.0.2.40 -U mlflow -d mlflow -c '\dt'

# 5. Train and register the first model
cd ..
./scripts/train-and-register.sh          # → Staging
./scripts/train-and-register.sh --promote  # → Production (first model, manual gate)

# 6. Deploy the serving layer
kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/fastapi/
kubectl apply -f kubernetes/hpa.yml

# 7. Smoke test
API_BASE_URL=http://<ingress-ip> ./scripts/smoke-test.sh

# 8. Verify monitoring
curl http://10.0.2.50:9090/-/healthy
curl http://10.0.2.51:3000/api/health
```

`scripts/bootstrap.sh` wraps steps 1–3. The `Makefile` mirrors every step:
`make provision`, `make inventory`, `make configure`, `make bootstrap`, `make train`,
`make evaluate`, `make promote`, `make test`, `make build-image`, `make deploy-k8s`,
`make smoke`, `make validate`.

## Verifying each layer

| Layer | Check | Expected |
|---|---|---|
| Kubernetes | `kubectl get nodes` | 3 nodes `Ready` |
| Namespace | `kubectl get all -n mlops` | `deployment/fastapi`, `service/fastapi`, HPA |
| MLflow | open `http://10.0.2.30:5000` | experiment `churn_prediction` with runs |
| Registry | `mlflow models list` / Registry UI | `churn-model` with a `Production` version |
| API | `curl http://<ingress>/health` | `{"status":"healthy","model_loaded":true,...}` |
| Model in use | `curl http://<ingress>/model-info` | the version you promoted |
| Metrics | `curl http://<ingress>/metrics` | Prometheus text exposition |
| Prometheus | `http://10.0.2.50:9090/targets` | all targets `UP` |
| Grafana | `http://10.0.2.51:3000` | four dashboards with live data |

## Triggering a retrain via CI/CD

The Jenkins pipeline (`cicd/Jenkinsfile`, running on VM02) has these stages:

1. **Checkout** — on push to `main`, or on the retraining schedule.
2. **Train** (`cicd/stages/train.sh`) — runs `ml/training/train.py` and then
   `ml/evaluation/evaluate.py`. Evaluation exits non-zero if F1 regresses by more than 1%
   against the current `Production` model, which fails the build before anything is
   promoted.
3. **Register & Promote** — a Jenkins `input` step asks for the MLflow model version and
   waits for a human approval, then transitions that version to `Production`.
4. **Test** (`cicd/stages/test.sh`) — `pytest api/tests`.
5. **Build** (`cicd/stages/build.sh`) — builds and tags the FastAPI image (code only).
6. **Push** — pushes the tagged image to the registry.
7. **Deploy** (`cicd/stages/deploy.sh`) — `kubectl set image` +
   `kubectl rollout restart deployment/fastapi -n mlops`, so every pod re-pulls the newly
   promoted `Production` model on startup.
8. **Smoke test** (`scripts/smoke-test.sh`) — POSTs a known sample to `/predict` and checks
   for a 200 with a probability in `[0, 1]`.

To retrain manually without touching the pipeline:

```bash
make train      # train + register + Staging
make evaluate   # gate: exits 2 if F1 regressed too far
make promote    # manual gate: Staging → Production
kubectl rollout restart deployment/fastapi -n mlops
```

## Rolling back

Rollback is a registry operation, not an image operation — the image contains no model:

```bash
# Point Production back at the previous version
python3 - <<'EOF'
from mlflow.tracking import MlflowClient
c = MlflowClient()
c.transition_model_version_stage("churn-model", <previous_version>, "Production")
EOF

kubectl rollout restart deployment/fastapi -n mlops
```

To roll back a *code* change instead, use `kubectl rollout undo deployment/fastapi -n mlops`.

## Tearing down

```bash
make clean               # local artifacts only
cd terraform && terraform destroy
```
