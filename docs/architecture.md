# Architecture

This document records the component layout of the platform and — more importantly — the
two architectural decisions the build specification deliberately left open, along with the
choice that was made and why.

## Component diagram

```
                              ┌──────────────────────────┐
                              │         Internet          │
                              └────────────┬─────────────┘
                                           │ 80/443
                              ┌────────────▼─────────────┐
                              │  Public subnet 10.0.1.0/24 │
                              │  Ingress / LB entrypoint    │
                              └────────────┬─────────────┘
                                           │
 ┌─────────────────────────────────────────▼──────────────────────────────────────────┐
 │                        Private subnet 10.0.2.0/24                                    │
 │                                                                                      │
 │   ┌────────────────────────────────────────────┐                                     │
 │   │ Kubernetes cluster (namespace: mlops)        │                                     │
 │   │  VM03 k8s-cp   10.0.2.20  control plane      │                                     │
 │   │  VM04 k8s-wk1  10.0.2.21  worker             │                                     │
 │   │  VM05 k8s-wk2  10.0.2.22  worker             │                                     │
 │   │                                              │                                     │
 │   │   Deployment/fastapi (2+ replicas, HPA)      │───┐ pulls model at pod startup      │
 │   │   Service/fastapi  ClusterIP :80             │   │                                 │
 │   │   Ingress/fastapi  api.mlops.local           │   │                                 │
 │   └──────────────────────────────────────────────┘   │                                 │
 │                       │ writes every prediction      │                                 │
 │                       ▼                              ▼                                 │
 │   ┌──────────────────────────┐        ┌────────────────────────────────┐               │
 │   │ VM08 postgres 10.0.2.40   │◄───────│ VM06 mlflow 10.0.2.30 :5000     │               │
 │   │  db mlops   (predictions, │ backend│  Tracking server + Registry     │               │
 │   │             model_metadata)│  store │  artifacts on local disk        │               │
 │   │  db mlflow  (MLflow store) │        └────────────────────────────────┘               │
 │   └──────────────────────────┘                    ▲                                     │
 │                                                   │ logs runs, registers versions       │
 │   ┌──────────────┐  ┌──────────────┐  ┌───────────┴──────┐  ┌──────────────┐            │
 │   │ VM01 ctrl-node│  │ VM02 git-cicd │  │ VM11 training-env │  │ VM12 testing-env│         │
 │   │ 10.0.2.10     │  │ 10.0.2.11     │  │ 10.0.2.60          │  │ 10.0.2.61       │        │
 │   │ Terraform +   │  │ Jenkins :8080  │  │ runs ml/training/* │  │ runs api/tests, │        │
 │   │ Ansible       │  │               │  │                    │  │ load tests      │        │
 │   └──────────────┘  └──────────────┘  └──────────────────┘  └──────────────┘            │
 │                                                                                      │
 │   ┌────────────────────────┐   ┌────────────────────────┐   ┌────────────────────┐     │
 │   │ VM09 prometheus 10.0.2.50│   │ VM10 grafana 10.0.2.51 │   │ VM07 fastapi (opt.) │     │
 │   │ :9090 scrapes everything │◄──│ :3000 dashboards        │   │ 10.0.2.31 build host│     │
 │   └────────────────────────┘   └────────────────────────┘   └────────────────────┘     │
 └──────────────────────────────────────────────────────────────────────────────────────┘
```

`node_exporter` (`:9100`) runs on all 12 VMs; `postgres_exporter` (`:9187`) runs on VM08.

## Decision 1 — where FastAPI runs

The original brief describes both a dedicated FastAPI VM (VM07) and "deploy every component
inside Kubernetes". Code generation needs one authoritative answer.

**Decision: FastAPI runs as a Kubernetes `Deployment` + `Service` + `Ingress` on VM03-05.**

Rationale:

- The serving layer is stateless — the model is fetched from the MLflow Registry at pod
  startup — so it is exactly the workload type that benefits from replicas, rolling updates
  and horizontal autoscaling.
- The CI/CD flow in the brief (`Build Docker Image → Deploy to Kubernetes → REST API`) only
  makes sense with the API in-cluster; a standalone VM would need a bespoke deploy step.
- `kubernetes/hpa.yml` can then scale on CPU/request rate, which is what the load-test
  acceptance criterion exercises.

**VM07 is retained as an optional Docker build/test host** — used to build and smoke-test the
image locally before it is pushed and rolled out to the cluster. It is not part of the serving
path. It can be dropped from `terraform/variables.tf` without affecting anything else.

Implementation: `kubernetes/fastapi/{deployment,service,configmap,secret,ingress}.yml`,
`kubernetes/hpa.yml`.

## Decision 2 — where MLflow runs

**Decision: MLflow runs standalone on VM06, not in Kubernetes.**

Rationale:

- MLflow's tracking server is stateful: it owns an artifact store on disk and a backend
  database. Running it in-cluster would require a `StatefulSet` plus a `PersistentVolume`
  with a real storage class — infrastructure complexity that adds nothing to the ML story
  at this scope.
- Keeping the registry outside the cluster means a full cluster rebuild never risks the
  experiment history or the registered model versions.
- The backend store is PostgreSQL on VM08 (database `mlflow`), *not* the default SQLite, so
  even a VM06 rebuild preserves run history:
  `mlflow server --backend-store-uri postgresql://mlflow:***@10.0.2.40/mlflow`.

Implementation: `ansible/roles/mlflow`, `ansible/playbooks/04-mlflow.yml`,
`docker/mlflow/Dockerfile`.

## Decision 3 — the model is never baked into the image

The FastAPI Docker image contains **code only**. `api/app/model_loader.py` calls
`mlflow.pyfunc.load_model("models:/churn-model/Production")` during the FastAPI `lifespan`
startup hook, using `MLFLOW_TRACKING_URI` supplied by `kubernetes/fastapi/configmap.yml`.

Consequences:

- Promoting a new model version to `Production` requires no image rebuild — only
  `kubectl rollout restart deployment/fastapi -n mlops`.
- Image tags track *code* changes, model versions track *model* changes; the two lifecycles
  stay independent.
- A model-load failure must not crash the pod. `load_model()` catches and logs the error,
  `/health` then reports `degraded` (or `unhealthy` if the database is also down), and the
  readiness probe keeps the pod out of the Service until a model is available.

## Decision 4 — model promotion is a manual gate

`train.py` registers the new version and transitions it to `Staging` automatically.
`ml/evaluation/evaluate.py` compares it against the current `Production` model and fails if
F1 regresses by more than `evaluation.max_f1_regression` (1%, in `ml/training/config.yml`).
The transition to `Production` is a Jenkins approval step, driven by
`scripts/train-and-register.sh --promote`.

This is deliberately not fully automatic: an approval gate is the realistic guardrail for a
model that affects customers, and it makes the registry stage transitions auditable.

## Data flow at request time

1. Client `POST /predict` → Ingress → Service → one of the FastAPI pods.
2. The pod validates the body against `api/app/schemas.py` (`PredictRequest`).
3. The payload becomes a one-row `pandas.DataFrame` and is passed to the pyfunc model, whose
   wrapper (`ChurnModelWrapper` in `ml/training/train.py`) returns `prediction` +
   `probability`.
4. The request, prediction, probability, model name/version/stage and latency are inserted
   into the `predictions` table on VM08. A failure here is logged and rolled back but does
   **not** fail the request — the audit log is not on the critical path.
5. `prometheus-fastapi-instrumentator` records the request in `/metrics`, which Prometheus
   on VM09 scrapes through the Kubernetes Service.

## Related documents

- Infrastructure and IP plan: [`infrastructure-diagram.md`](infrastructure-diagram.md)
- Training-to-deployment flow: [`ml-pipeline-diagram.md`](ml-pipeline-diagram.md)
- Bootstrap sequence: [`deployment-guide.md`](deployment-guide.md)
