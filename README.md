# Enterprise MLOps Platform

End-to-end MLOps lab: 12-VM single-cloud infrastructure, Kubernetes serving layer,
MLflow model registry, Prometheus/Grafana monitoring, and a Jenkins CI/CD pipeline.

## What it does

- **Infrastructure as Code** (Terraform): 12 VMs in a private `10.0.2.0/24` subnet
  with a public `10.0.1.0/24` ingress subnet and per-tier firewall rules
  (GCP by default, provider overridable).
- **Configuration management** (Ansible): Kubernetes cluster (1 control plane +
  2 workers), MLflow tracking server, PostgreSQL (app DB + MLflow backend store),
  Jenkins, Prometheus + Grafana, node_exporter on every VM.
- **ML pipeline** (scikit-learn): Telco Customer Churn binary classification,
  ~7k synthetic rows in `ml/data/raw/telco_churn.csv`. Training logs params/metrics
  to MLflow and registers `churn-model`; promotion to `Staging` is automatic, to
  `Production` it is a manual gate.
- **Serving** (FastAPI): `POST /predict`, `GET /health`, `GET /model-info`.
  The model is pulled from the MLflow Model Registry at container startup (never
  baked into the image). Every prediction is logged to PostgreSQL.
- **Monitoring**: Prometheus scrapes node_exporter (all VMs), FastAPI, and
  postgres_exporter; Grafana dashboards for node metrics, cluster, FastAPI
  request/error/latency, and model performance.
- **CI/CD** (Jenkins): checkout → train → evaluate → manual promotion approval →
  test → build image → deploy to Kubernetes → smoke test.

## Key decisions (see `docs/architecture.md`)

| Decision | Choice |
|---|---|
| Cloud provider | Google Cloud Platform (default; overridable in Terraform) |
| ML problem | Customer Churn (tabular, binary) |
| ML framework | scikit-learn `RandomForestClassifier` |
| FastAPI location | Kubernetes Deployment on the 3-node cluster (VM07 optional/standalone) |
| MLflow location | Standalone on VM06 (stateful, simplest) |
| CI/CD | Jenkins on VM02 |
| Model promotion | Staging automatic, Production manual (approval gate) |

## Repository layout

```
terraform/    GCP VPC, firewalls, 12 VMs (modules: network, security-groups, compute)
ansible/      Inventory + site.yml + 7 playbooks + 11 roles
docker/       fastapi / mlflow / training images
kubernetes/   mlops namespace, fastapi deployment/service/configmap/secret/ingress, HPA
ml/           data, EDA notebook, training pipeline, evaluation
api/          FastAPI app (model_loader, routers, db, metrics)
monitoring/   Prometheus config + alert rules, Grafana dashboards
scripts/      bootstrap, inventory generator, train-and-register, smoke test
cicd/         Jenkinsfile + pipeline stages
docs/         Architecture, diagrams, guides, troubleshooting (see docs/)
```

## Quickstart

```bash
# 1. Provision infrastructure
cd terraform
terraform init
terraform apply -auto-approve

# 2. Generate Ansible inventory from the IP plan
cd ../scripts
python3 generate-inventory.py > ../ansible/inventory/hosts.ini

# 3. Configure everything
cd ../ansible
ansible-playbook -i inventory/hosts.ini site.yml

# 4. Verify MLflow + Postgres
curl http://10.0.2.30:5000/health
psql -h 10.0.2.40 -U mlflow -d mlflow -c '\dt'

# 5. Train and register the first model (manual promotion gate)
../scripts/train-and-register.sh

# 6. Deploy the FastAPI serving layer to Kubernetes
kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/fastapi/
kubectl apply -f kubernetes/hpa.yml

# 7. Smoke test
./scripts/smoke-test.sh

# 8. Verify monitoring
curl http://10.0.2.50:9090/-/healthy
curl http://10.0.2.51:3000/api/health
```

`scripts/bootstrap.sh` wraps steps 1-3. A `Makefile` mirrors the same targets.

See `docs/` for architecture diagrams, deployment guide, API documentation,
training guide, and troubleshooting.

## Model promotion workflow

```
train.py  →  registers version in MLflow Registry + transitions to Staging
evaluate.py → compares new model against current Production (F1 tolerance)
train-and-register.sh --promote  →  manual approval → Production
```

## Verification

```bash
make validate        # py_compile all python, YAML/JSON lint, terraform validate, ansible syntax-check
make train           # run training pipeline end-to-end (needs MLflow reachable)
make smoke           # POST a sample to /predict
```

## License

Lab/portfolio project. No warranty.
