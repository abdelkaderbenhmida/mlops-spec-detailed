# Architecture

This document records the component layout of Anvil — the air-gapped predictive maintenance
platform — and — more importantly — the architectural decisions the build specification
deliberately left open, along with the choice that was made and why.

## Component diagram

```
╔══════════ Level 0-2: OT Network — NO OUTBOUND CONNECTIVITY ══════════╗
║   [Sensors] ── [PLCs] ── [SCADA / Historian: PI, Ignition, Wonderware] ║
║                                    │                                   ║
║                                    │ OPC-UA (read-only)                ║
╚════════════════════════════════════│═══════════════════════════════════╝
                                     │  DATA DIODE or strictly one-way
                                     ▼  firewall rule — OT never accepts
╔══════════ Level 3.5: DMZ — ANVIL PLATFORM (10.20.2.0/24) ════════════╗
║                                                                        ║
║   ┌────────────────────────────────────────────┐                       ║
║   │ Kubernetes cluster (namespace: mlops)        │                       ║
║   │  VM03 k8s-cp   10.20.2.20  control plane      │                       ║
║   │  VM04 k8s-wk1  10.20.2.21  worker             │                       ║
║   │  VM05 k8s-wk2  10.20.2.22  worker             │                       ║
║   │  Deployment/inference (2+ replicas, HPA)      │◄─ pulls model at      ║
║   │  Deployment/alerting (tier engine + CMMS)     │   pod startup         ║
║   │  Ingress  api.mlops.local                     │                       ║
║   └──────────────────────────────────────────────┘                       ║
║                       │ writes predictions/alerts                        ║
║                       ▼                                                  ║
║   ┌──────────────────────────┐        ┌────────────────────────────┐     ║
║   │ VM08 timescale 10.20.2.40 │◄───────│ VM06 mlflow 10.20.2.30 :5000│     ║
║   │  TimescaleDB: sensor_     │ backend│  Tracking server + Registry │     ║
║   │  telemetry (hypertable),  │  store │  artifacts on local disk/NAS│     ║
║   │  predictions, alerts,     │        └────────────────────────────┘     ║
║   │  feedback, mlflow db      │        ▲                                  ║
║   └──────────────────────────┘        │ logs runs, registers versions     ║
║                    ▲                  │                                   ║
║                    │ writes telemetry │                                   ║
║   ┌──────────────────────────┐        └───────────────────────┐           ║
║   │ VM07 ingest 10.20.2.31   │   ┌──────────────┐  ┌───────────┴────────┐  ║
║   │ OPC-UA client (read-only,│   │ VM11 training │  │ VM12 registry-      │  ║
║   │ egress-only), store-and- │   │ 10.20.2.60     │  │ mirror 10.20.2.61  │  ║
║   │ forward buffer, tag map  │   │ GPU-optional   │  │ Harbor + devpi +   │  ║
║   └──────────────────────────┘   └────────────────┘  │ aptly + charts    │  ║
║   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐└───────────────────┘  ║
║   │ VM01 ctrl-node│  │ VM02 gitea-   │  │ VM09 prometheus│  ┌──────────────┐  ║
║   │ 10.20.2.10    │  │ jenkins       │  │ 10.20.2.50     │  │ VM10 grafana │  ║
║   │ Terraform +   │  │ 10.20.2.11    │  │ scrapes        │  │ 10.20.2.51   │  ║
║   │ Ansible       │  │ Git + CI local│  │ everything     │  │ dashboards + │  ║
║   └──────────────┘  └──────────────┘  └────────────────┘  │ wall display │  ║
║                                                           └──────────────┘  ║
╚════════════════════════════════════│════════════════════════════════════════╝
                                    │  scheduled export, reviewed
                                    ▼  aggregates only — never raw signals
╔══════════ Level 4-5: Enterprise IT ════════════════════════════════════════╗
║   CMMS (work orders) · Corporate BI · Multi-plant fleet reporting           ║
╚════════════════════════════════════════════════════════════════════════════╝
```

`node_exporter` (`:9100`) runs on all 12 VMs; `timescale_exporter` (`:9187`) runs on VM08;
an ingestion exporter (tag rate, buffer depth, unmapped tags) runs on VM07. There is no
internet-facing element anywhere — no public subnet, no load balancer, no cloud.

## Decision 1 — where the inference API runs

The original brief described both a dedicated FastAPI VM (VM07) and "deploy every component
inside Kubernetes". Code generation needs one authoritative answer.

**Decision: the inference API runs as a Kubernetes `Deployment` + `Service` + `Ingress` on
VM03-05.** VM07 is repurposed as the OPC-UA ingestion host (Decision 5), not a serving host.

Rationale:

- The serving layer is stateless — the model is fetched from the MLflow Registry at pod
  startup — so it is exactly the workload type that benefits from replicas, rolling updates
  and horizontal autoscaling.
- The CI/CD flow (`Build Docker Image → Deploy to Kubernetes → REST API`) only makes sense
  with the API in-cluster; a standalone VM would need a bespoke deploy step.
- `kubernetes/hpa.yml` can then scale on CPU/request rate.

Implementation: `kubernetes/inference/{deployment,service,configmap,secret,ingress}.yml`,
`kubernetes/hpa.yml`.

## Decision 2 — where MLflow runs

**Decision: MLflow runs standalone on VM06, not in Kubernetes.**

Rationale:

- MLflow's tracking server is stateful: it owns an artifact store on disk/NAS and a backend
  database. Running it in-cluster would require a `StatefulSet` plus a `PersistentVolume`
  with a real storage class — infrastructure complexity that adds nothing to the ML story.
- Keeping the registry outside the cluster means a full cluster rebuild never risks the
  experiment history or the registered model versions.
- The backend store is TimescaleDB on VM08 (database `mlflow`), *not* the default SQLite, so
  even a VM06 rebuild preserves run history:
  `mlflow server --backend-store-uri postgresql://mlflow:***@10.20.2.40/mlflow`.
- Artifact store is local disk (optionally a NAS mount) — there is no object storage in an
  air-gapped plant, and none is needed.

Implementation: `ansible/roles/mlflow`, `ansible/playbooks/04-mlflow.yml`,
`docker/mlflow/Dockerfile`.

## Decision 3 — the model is never baked into the image

The inference Docker image contains **code only**. `api/app/model_loader.py` calls
`mlflow.pyfunc.load_model("models:/anvil-health/Production")` during the FastAPI `lifespan`
startup hook, using `MLFLOW_TRACKING_URI` supplied by `kubernetes/inference/configmap.yml`.

Consequences:

- Promoting a new model version to `Production` requires no image rebuild — only
  `kubectl rollout restart deployment/inference -n mlops`.
- Image tags track *code* changes, model versions track *model* changes; the two lifecycles
  stay independent.
- A model-load failure must not crash the pod. `load_model()` catches and logs the error,
  `/health` then reports `degraded` (or `unhealthy` if the database is also down), and the
  readiness probe keeps the pod out of the Service until a model is available.

## Decision 4 — model promotion is a manual gate

`train.py` registers the new version and transitions it to `Staging` automatically.
`ml/evaluation/evaluate.py` compares it against the current `Production` model and fails if
alert precision regresses by more than the tolerance in `ml/training/config.yml`. The
transition to `Production` is a Jenkins approval step, driven by
`scripts/train-and-register.sh --promote`.

This is deliberately not fully automatic: an approval gate is the realistic guardrail for a
model whose alerts trigger line stops and maintenance spend, and it makes the registry stage
transitions auditable.

## Decision 5 — ingestion runs on VM07 (OPC-UA, one-way)

The original spec had no data acquisition layer. In an industrial deployment that is the
component most likely to sink the project, so it is now a first-class host:

- **OPC-UA client** on VM07 subscribes read-only to tags from the plant historian/SCADA.
- **One-directional by construction**: the OT network never accepts a connection from the
  DMZ. A hardware data diode where policy demands it; otherwise strict egress-only firewall
  rules (`sg-ot-egress`) with no return path beyond TCP acknowledgements and the residual
  risk documented.
- **Store-and-forward buffering** on VM07 so historian maintenance windows do not corrupt
  training sets.
- **Tag mapping is versioned configuration** (`ml/ingest/tag_mapping.yml`); unmapped tags
  are alerted on, never silently dropped.

Implementation: `ansible/roles/ingest`, `ansible/playbooks/08-ingest.yml`,
`ml/ingest/opcua_client.py`.

## Decision 6 — TimescaleDB, not vanilla PostgreSQL

The original chose PostgreSQL on VM08. Still PostgreSQL — but sensor data at 200 sensors ×
1 Hz × 24/7 ≈ 17M points/day/machine will not perform in vanilla Postgres, and compression
materially changes the storage budget. TimescaleDB adds hypertables, continuous aggregates
(`hourly_stats`), and native compression. The original relational schema (predictions,
model_metadata) survives unchanged; new tables for telemetry, alerts, and the
work-order feedback loop are documented in the main spec §8.

Implementation: `ansible/roles/timescaledb`, `ansible/playbooks/05-timescaledb.yml`.

## Decision 7 — VM12 is the offline mirror

Testing-env was the weakest use of a 12-VM budget in the original plan. VM12 now hosts the
offline artifact mirror — Harbor (containers), devpi (PyPI), aptly (APT), a Helm chart
museum, and a Terraform provider mirror. Nothing in the plant installs or deploys without
going through VM12, and no `latest` tag exists anywhere in the platform. Update and bundle
procedures are specified in the main spec §11.

Implementation: `ansible/roles/mirror`, `ansible/playbooks/00-mirror.yml` (runs first),
`scripts/import-update-bundle.sh`.

## Data flow at request time

1. Plant historian publishes tags → VM07 OPC-UA client (read-only, egress-only conduit)
   → store-and-forward buffer → TimescaleDB `sensor_telemetry` hypertable.
2. The tiered alerting engine (`kubernetes/alerting/`) scores each machine's latest window
   with the Production model; a Plan/Urgent/Stop tier creates a CMMS work order and a
   notification with an explanation (§7.2 of the main spec).
3. Client `POST /predict` → Ingress → Service → one of the inference pods. The pod
   validates the window against `api/app/schemas.py`, passes it to the pyfunc model, and
   returns `health_score`, `tier`, `rul_days` (uncertainty band) and `explanation`.
4. The request and response are inserted into the `predictions` table on VM08. A failure
   here is logged and rolled back but does **not** fail the request — the audit log is not
   on the critical path.
5. The technician closes the work order on the plant CMMS; the feedback bridge
   (`api/app/cmms.py`) writes the structured outcome into `work_order_feedback` — the
   label-acquisition loop that trains the next model version.
6. `prometheus-fastapi-instrumentator` records the request in `/metrics`, which Prometheus
   on VM09 scrapes through the Kubernetes Service.

## Related documents

- Infrastructure and IP plan: [`infrastructure-diagram.md`](infrastructure-diagram.md)
- Training-to-deployment flow: [`ml-pipeline-diagram.md`](ml-pipeline-diagram.md)
- Bootstrap sequence: [`deployment-guide.md`](deployment-guide.md)
