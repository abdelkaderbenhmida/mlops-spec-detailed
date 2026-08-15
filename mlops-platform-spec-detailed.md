# Project: Enterprise MLOps Platform — Detailed Build Specification

> Implementation-ready expansion of the original brief: concrete IP plan, file-level repo
> layout, the exact ML pipeline stages, MLflow/FastAPI/K8s wiring, and monitoring targets
> specific to model-serving metrics. Intended to be fed to an AI coding assistant (or
> followed manually) to generate the actual code.

---

## 1. High-Level Architecture

```
                         ┌────────────────────┐
                         │      Internet         │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  VM07 FastAPI Server  │──── serves /predict, reads model
                         │  (or in-cluster if K8s │     from MLflow Model Registry
                         │   is the serving target)│     at container startup / on reload
                         └──────────┬──────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                            │                            │
┌───────▼────────┐        ┌─────────▼─────────┐        ┌────────▼────────┐
│ VM06 MLflow      │        │ VM03-05 Kubernetes  │        │ VM08 PostgreSQL   │
│ Tracking Server + │        │ (CP + 2 workers)     │        │ (app DB: users,   │
│ Model Registry     │        │ hosts FastAPI +      │        │ predictions,      │
│ (artifact store on │        │ possibly MLflow too   │        │ MLflow backend    │
│ VM06 disk or S3)    │        │                        │        │ store option)      │
└─────────────────────┘        └────────────────────────┘        └────────────────────┘

┌────────────────┐   ┌────────────────┐   ┌───────────────────┐   ┌──────────────────┐
│ VM01 TF+Ansible  │   │ VM02 Git+CI/CD  │   │ VM09 Prometheus    │   │ VM10 Grafana       │
└──────────────────┘   └──────────────────┘   └─────────────────────┘   └──────────────────┘

┌────────────────────┐  ┌────────────────────┐
│ VM11 Training env    │  │ VM12 Testing env     │
│ (runs ml/training/*)  │  │ (runs pytest, load    │
│                        │  │  test /predict)        │
└────────────────────────┘  └────────────────────────┘
```

**Key architectural decision to state explicitly in `docs/architecture.md`:**
Decide **where FastAPI actually runs**: standalone on VM07 (simpler, matches the VM table
literally) vs **as a Kubernetes Deployment** on VM03-05 (matches "Deploy every component
inside Kubernetes" in the Core Technologies section, and matches the pipeline diagram's
"Build Docker Image → Deploy to Kubernetes → REST API" flow). **Recommended: deploy FastAPI
as a Kubernetes Deployment+Service+Ingress**, and treat VM07 as decommissioned/optional, OR
repurpose VM07 as a Docker host used only during local image-build/test before pushing to the
cluster. Document whichever choice is made — the brief has both, and code generation needs
one authoritative answer. Same logic applies to MLflow (VM06 standalone vs in-cluster) —
recommended: **MLflow standalone on VM06** (it's stateful and simpler to keep outside K8s
for a project of this scope), while FastAPI (stateless, benefits from replicas/rolling
updates) goes into Kubernetes.

---

## 2. Network Plan

| Item | Value |
|---|---|
| VPC/VNet | `10.0.0.0/16` |
| Public subnet | `10.0.1.0/24` (Ingress/LB entrypoint only) |
| Private subnet | `10.0.2.0/24` (everything else) |
| SSH | key-based only, via bastion if added, or directly to mgmt subnet if scope is kept small (this brief has no dedicated bastion VM — recommend adding SSH hardening + a jump-capable VM01 instead of a full bastion tier, given the 12-VM budget) |

### IP Allocation

| VM | Hostname | IP | Ports |
|---|---|---|---|
| VM01 | ctrl-node | 10.0.2.10 | 22 |
| VM02 | git-cicd | 10.0.2.11 | 22, 8080 (Jenkins) or 3000 (Gitea) |
| VM03 | k8s-cp | 10.0.2.20 | 22, 6443, 2379-2380, 10250-10259 |
| VM04 | k8s-wk1 | 10.0.2.21 | 22, 10250, 30000-32767 |
| VM05 | k8s-wk2 | 10.0.2.22 | 22, 10250, 30000-32767 |
| VM06 | mlflow | 10.0.2.30 | 22, 5000 |
| VM07 | fastapi (optional/standalone) | 10.0.2.31 | 22, 8000 |
| VM08 | postgres | 10.0.2.40 | 22, 5432 |
| VM09 | prometheus | 10.0.2.50 | 22, 9090 |
| VM10 | grafana | 10.0.2.51 | 22, 3000 |
| VM11 | training-env | 10.0.2.60 | 22 |
| VM12 | testing-env | 10.0.2.61 | 22 |

### Security Groups

- `sg-mgmt`: 22 from admin IP.
- `sg-internal`: all traffic within `10.0.2.0/24`.
- `sg-k8s`: 6443/2379-2380/10250-10259/NodePort range, internal only.
- `sg-public`: 80/443 from internet, forwards to Ingress NodePort or LB.

---

## 3. Repository Structure (file-level)

```
mlops-platform/
├── README.md
├── Makefile
├── .gitignore
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── backend.tf
│   ├── terraform.tfvars.example
│   └── modules/
│       ├── network/
│       ├── security-groups/
│       └── compute/
│
├── ansible/
│   ├── ansible.cfg
│   ├── inventory/
│   │   ├── hosts.ini
│   │   └── group_vars/
│   │       ├── all.yml
│   │       ├── k8s.yml
│   │       └── mlflow.yml
│   ├── site.yml
│   ├── playbooks/
│   │   ├── 01-common.yml
│   │   ├── 02-docker.yml
│   │   ├── 03-kubernetes.yml
│   │   ├── 04-mlflow.yml
│   │   ├── 05-postgresql.yml
│   │   ├── 06-cicd.yml               # Jenkins or Gitea+Actions runner
│   │   └── 07-monitoring.yml
│   └── roles/
│       ├── common/
│       ├── docker/
│       ├── k8s-common/
│       ├── k8s-control-plane/
│       ├── k8s-worker/
│       ├── mlflow/
│       ├── postgresql/
│       ├── cicd/
│       ├── prometheus/
│       ├── node_exporter/
│       └── grafana/
│
├── docker/
│   ├── fastapi/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── mlflow/
│   │   └── Dockerfile                # if containerizing MLflow rather than bare install
│   └── training/
│       └── Dockerfile                # reproducible training image (pinned Python + libs)
│
├── kubernetes/
│   ├── namespace.yml                 # mlops
│   ├── fastapi/
│   │   ├── deployment.yml
│   │   ├── service.yml
│   │   ├── configmap.yml             # MLFLOW_TRACKING_URI, MODEL_NAME, MODEL_STAGE
│   │   ├── secret.yml                # DB creds
│   │   └── ingress.yml
│   └── hpa.yml                       # optional: autoscale FastAPI on CPU or request rate
│
├── ml/
│   ├── data/
│   │   ├── raw/                      # raw dataset (or a fetch script, not committed if large)
│   │   └── processed/
│   ├── notebooks/
│   │   └── 01-eda.ipynb
│   ├── training/
│   │   ├── train.py                  # loads data, trains, logs to MLflow, registers model
│   │   ├── preprocess.py
│   │   ├── features.py
│   │   └── config.yml                # hyperparameters, dataset path, MLflow experiment name
│   ├── evaluation/
│   │   └── evaluate.py               # computes metrics, compares to current "Production" model
│   └── models/
│       └── .gitkeep                  # local scratch only; source of truth is MLflow registry
│
├── api/
│   ├── main.py                       # FastAPI app entrypoint
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── model_loader.py           # loads model from MLflow Registry by name+stage
│   │   ├── schemas.py                # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── predict.py
│   │   │   └── health.py
│   │   ├── db.py                     # SQLAlchemy engine/session for logging predictions
│   │   └── metrics.py                # prometheus_fastapi_instrumentator setup
│   └── tests/
│       ├── test_predict.py
│       └── test_health.py
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alert.rules.yml
│   └── grafana/
│       └── dashboards/
│           ├── node-exporter.json
│           ├── kubernetes-cluster.json
│           ├── fastapi-requests.json
│           └── model-performance.json
│
├── scripts/
│   ├── bootstrap.sh
│   ├── generate-inventory.py
│   ├── train-and-register.sh         # runs ml/training/train.py, tags model, promotes stage
│   └── smoke-test.sh                 # curl POST /predict with a sample payload
│
├── cicd/
│   ├── Jenkinsfile                   # or .github/workflows/ if using GitHub Actions runner on VM02
│   └── stages/
│       ├── train.sh
│       ├── test.sh
│       ├── build.sh
│       └── deploy.sh
│
└── docs/
    ├── architecture.md
    ├── ml-pipeline-diagram.md
    ├── infrastructure-diagram.md
    ├── deployment-guide.md
    ├── api-documentation.md
    ├── training-guide.md
    └── troubleshooting.md
```

---

## 4. Machine Learning Choice (concrete, so code generation isn't ambiguous)

**Recommended default for a first build:** *Customer Churn Prediction* — tabular data,
binary classification, fast to train, easy to explain in a portfolio, works well with
scikit-learn or XGBoost (no GPU needed, keeps infra simple as the brief intends).

- **Dataset**: e.g. the public Telco Customer Churn dataset (~7,000 rows, CSV) — small enough
  to commit a preprocessed sample or fetch via script in `ml/data/`.
- **Framework**: `scikit-learn` (`RandomForestClassifier` or `LogisticRegression` baseline)
  or `XGBoost` for a slightly stronger model — pick one, document it, don't implement both
  unless comparing is explicitly a learning goal.
- **Target metric**: F1 score and ROC-AUC (churn is typically imbalanced) logged to MLflow.
- **Features**: tenure, monthly charges, contract type, payment method, etc. — standard
  one-hot/ordinal encoding in `ml/training/features.py`.

If a different domain is preferred (house price, fraud, heart disease), the same file
structure applies — only `ml/training/*.py` and `api/app/schemas.py` (request/response
shape) change.

---

## 5. Machine Learning Pipeline (concrete steps → files)

| Pipeline stage | File | Detail |
|---|---|---|
| Dataset | `ml/data/raw/` | committed sample or fetched by `scripts/train-and-register.sh` |
| Data validation | `ml/training/preprocess.py` | schema check (expected columns, dtypes, null thresholds) |
| Preprocessing | `ml/training/preprocess.py` | imputation, encoding, train/test split (stratified) |
| Feature engineering | `ml/training/features.py` | derived features, scaling if needed |
| Train model | `ml/training/train.py` | `mlflow.start_run()`, fit model, `mlflow.log_param(...)` for hyperparams |
| Evaluate model | `ml/evaluation/evaluate.py` | compute metrics, `mlflow.log_metric(...)`, optionally compare against current Production-stage model before allowing promotion |
| MLflow logging | `train.py` | `mlflow.sklearn.log_model()` (or `mlflow.xgboost`) with the full run |
| Register model | `train.py` or `scripts/train-and-register.sh` | `mlflow.register_model()`, transition stage to `Staging`, manual/automatic promotion to `Production` after evaluation passes threshold |
| Build Docker image | CI/CD stage `build.sh` | builds `docker/fastapi/Dockerfile`, image contains code only — model is pulled from MLflow Registry **at container startup**, not baked in, so new model versions don't require a rebuild |
| Deploy to Kubernetes | CI/CD stage `deploy.sh` | `kubectl set image` or `kubectl rollout restart` (to force re-pull of latest Production model) |
| REST API | `api/app/routers/predict.py` | `POST /predict` |
| Monitoring | `api/app/metrics.py` + Prometheus | request count/latency, and optionally prediction distribution for drift-awareness (see §7) |

---

## 6. FastAPI Model Server — Concrete Contract

```
POST /predict
Request body (example, churn model):
{
  "tenure_months": 12,
  "monthly_charges": 70.5,
  "contract_type": "month-to-month",
  "payment_method": "electronic_check",
  ...
}

Response:
{
  "prediction": "churn" | "no_churn",
  "probability": 0.83,
  "model_version": "7",
  "model_stage": "Production"
}
```

- `GET /health` — checks DB connectivity + that a model is loaded; used as K8s
  readiness/liveness probe.
- `GET /model-info` — returns currently loaded model name/version/stage (useful for
  debugging which model is actually serving).
- `app/model_loader.py` — on startup, calls
  `mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")` using
  `MLFLOW_TRACKING_URI` from env/ConfigMap; optionally reload on a timer or via an
  admin-triggered `/reload-model` endpoint so new Production promotions take effect without
  a pod restart.
- Every prediction request/response should be logged to PostgreSQL (`predictions` table:
  `id, input_json, prediction, probability, model_version, created_at`) for later analysis
  and potential drift detection.

---

## 7. Database Schema (PostgreSQL, VM08)

```sql
-- users: only if the API has auth; optional for a pure ML-serving lab
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  input_payload JSONB NOT NULL,
  prediction VARCHAR(50) NOT NULL,
  probability FLOAT,
  model_name VARCHAR(100),
  model_version VARCHAR(20),
  model_stage VARCHAR(20),
  latency_ms FLOAT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE model_metadata (
  id SERIAL PRIMARY KEY,
  model_name VARCHAR(100),
  version VARCHAR(20),
  stage VARCHAR(20),
  metrics JSONB,
  promoted_at TIMESTAMP DEFAULT now()
);
```

**MLflow backend store**: use this same PostgreSQL instance (a separate `mlflow` database)
for MLflow's tracking backend instead of the default SQLite, so experiment history survives
VM06 being rebuilt — configure via `mlflow server --backend-store-uri
postgresql://mlflow:***@10.0.2.40/mlflow --default-artifact-root <path or s3>`.

---

## 8. Monitoring — Concrete Targets

**Prometheus scrape configs:**
- `node_exporter` — all 12 VMs, port 9100.
- `kubernetes-nodes/pods/cadvisor` — via `kubernetes_sd_configs`.
- `fastapi` — `/metrics` endpoint exposed via `prometheus-fastapi-instrumentator` in
  `api/app/metrics.py`, scraped through the K8s Service.
- `mlflow` — MLflow doesn't expose Prometheus metrics natively; either front it with a
  small exporter sidecar or scrape `node_exporter` on VM06 only and rely on FastAPI +
  Postgres metrics for the ML-specific story (document this limitation).
- `postgres_exporter` — VM08, port 9187 (query counts, connection counts, table sizes for
  the `predictions` table growth).

**Grafana dashboards:**
- Node Exporter Full (ID 1860).
- Kubernetes Cluster (ID 315/7249).
- **FastAPI Requests**: request rate, error rate (4xx/5xx), p50/p95/p99 latency for `/predict`.
- **Model Performance**: prediction count over time, prediction class distribution (drift
  signal — a sudden shift in churn/no_churn ratio is worth alerting on), and — if periodic
  re-evaluation against labeled holdout data is implemented — accuracy/F1 trend over model
  versions (sourced from `model_metadata` table or MLflow API).

**Example alert rules:**
- `FastAPIHighErrorRate` — 5xx rate > 5% over 5m.
- `FastAPIHighLatency` — p95 > 500ms over 5m.
- `PredictionVolumeDrop` — prediction count drops to near-zero unexpectedly (possible upstream
  integration failure).
- `NoModelLoaded` — `/health` reporting no model loaded for > 2m.

---

## 9. CI/CD Pipeline (concrete stages)

Whether using Jenkins (VM02) or GitHub Actions with a self-hosted runner on VM02, the stages
are the same — encode in `cicd/Jenkinsfile` or `.github/workflows/pipeline.yml`:

1. **Checkout** — triggered on push to `main` or on a schedule (for periodic retraining).
2. **Train** (`cicd/stages/train.sh`) — runs `ml/training/train.py` on VM11 (training env)
   or as a Kubernetes `Job`; logs to MLflow (VM06); only proceeds if `ml/evaluation/evaluate.py`
   confirms the new model beats (or ties within tolerance) the current Production model.
3. **Register & Promote** — `mlflow models transition-stage` moves the new version to
   `Staging`; promotion to `Production` can be automatic (if metrics pass threshold) or
   manual (a pipeline approval gate) — recommend **manual approval gate** for a portfolio
   project since it demonstrates a realistic MLOps guardrail.
4. **Test** (`cicd/stages/test.sh`) — runs `api/tests/` (`pytest`) against a locally spun-up
   FastAPI instance pointed at the newly promoted model (or a Staging-stage model for
   pre-promotion testing).
5. **Build** (`cicd/stages/build.sh`) — builds and tags the FastAPI Docker image (code-only,
   model pulled at runtime — see §5).
6. **Deploy** (`cicd/stages/deploy.sh`) — pushes image, `kubectl set image` +
   `kubectl rollout restart deployment/fastapi -n mlops` so pods reload the latest
   Production model on startup.
7. **Smoke test** (`scripts/smoke-test.sh`) — POSTs a known sample to `/predict` post-deploy
   and checks for a 200 + sane response before marking the pipeline green.

---

## 10. Deployment Workflow (concrete commands)

```bash
# 1. Provision infrastructure
cd terraform
terraform init
terraform apply -auto-approve

# 2. Generate Ansible inventory
cd ../scripts
python3 generate-inventory.py > ../ansible/inventory/hosts.ini

# 3. Configure everything
cd ../ansible
ansible-playbook -i inventory/hosts.ini site.yml

# 4. Verify MLflow + Postgres
curl http://10.0.2.30:5000/health
psql -h 10.0.2.40 -U mlflow -d mlflow -c '\dt'

# 5. Train and register the first model
cd ../
./scripts/train-and-register.sh

# 6. Deploy the FastAPI serving layer to Kubernetes
kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/fastapi/

# 7. Smoke test
./scripts/smoke-test.sh

# 8. Verify monitoring
curl http://10.0.2.50:9090/-/healthy
curl http://10.0.2.51:3000/api/health
```

`scripts/bootstrap.sh` wraps steps 1–3; re-running `train-and-register.sh` on a schedule (or
via CI/CD trigger) demonstrates the "reproducible training" quality requirement.

---

## 11. Documentation Deliverables (contents checklist)

- `docs/architecture.md` — component diagram + the FastAPI-in-K8s-vs-standalone and
  MLflow-standalone-vs-in-cluster decisions (see §1).
- `docs/ml-pipeline-diagram.md` — the dataset → deployment flow (reuse the table in §5),
  including the manual-approval promotion gate.
- `docs/infrastructure-diagram.md` — VM table + IP plan (reuse §2).
- `docs/deployment-guide.md` — full bootstrap sequence + how to trigger a retrain via CI/CD.
- `docs/api-documentation.md` — `/predict`, `/health`, `/model-info` request/response
  examples (can largely mirror FastAPI's auto-generated OpenAPI docs at `/docs`, but written
  out for readers without a running instance).
- `docs/training-guide.md` — how to add a new feature, retrain locally, and what the
  promotion criteria are (e.g. "F1 must not regress by more than 1% vs current Production").
- `docs/troubleshooting.md` — MLflow artifact store permission issues, model load failures on
  pod startup, Postgres connection pool exhaustion, Prometheus scrape target down.

---

## 12. Suggested Build Order (incremental generation)

1. Terraform (network + compute, 12 VMs) → provision infrastructure.
2. Ansible `common` + `docker` + `k8s-*` roles → stand up the 3-node Kubernetes cluster.
3. Ansible `postgresql` role → VM08, create `mlops` and `mlflow` databases.
4. Ansible `mlflow` role → VM06, pointed at Postgres backend store.
5. `ml/` code (preprocessing, training, evaluation) → run once manually, confirm a model
   lands in the MLflow Registry.
6. `api/` code (FastAPI + model_loader + Postgres logging) + `docker/fastapi/Dockerfile`.
7. Kubernetes manifests (`kubernetes/fastapi/`) → deploy manually once, validate `/predict`.
8. CI/CD (`cicd/`) → automate steps 5–7 going forward.
9. Monitoring (`monitoring/`) + Grafana dashboards → last, since it depends on FastAPI/MLflow
   already emitting data.
10. Documentation, written last so it reflects what was actually built.

---

## 13. Open Decisions to Confirm Before Generating Code

- [ ] Cloud provider for Terraform (`aws`, `gcp`, `azure`, or local/libvirt for a no-cost lab)?
- [ ] ML domain/dataset: Customer Churn (recommended default) vs one of the other listed
      examples?
- [ ] Framework: scikit-learn vs XGBoost vs TensorFlow/PyTorch (only needed if the chosen
      problem benefits from deep learning — tabular churn/fraud/loan/house-price problems
      generally don't)?
- [ ] FastAPI deployment target: Kubernetes (recommended) vs standalone VM07?
- [ ] MLflow artifact store: local disk on VM06 vs S3/GCS-compatible object storage (matters
      more once running outside a single-VM lab)?
- [ ] CI/CD tool: Jenkins vs GitHub Actions with a self-hosted runner on VM02?
- [ ] Model promotion: automatic (metrics-gated) vs manual approval gate (recommended for
      portfolio realism)?
