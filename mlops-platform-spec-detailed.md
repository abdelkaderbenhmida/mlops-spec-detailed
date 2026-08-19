# Anvil — Enterprise MLOps Platform for Air-Gapped Industrial Plants — Detailed Build Specification

> Product: **Anvil** — on-premise predictive maintenance for manufacturing plants where
> production data is not permitted to leave the site.
>
> This is the implementation-ready expansion of the original brief, rewritten for the
> enterprise: concrete IP plan, file-level repo layout, the ML pipeline for remaining
> useful life (RUL) and anomaly detection on rotating equipment, OPC-UA ingestion,
> air-gap operations, tiered alerting, TimescaleDB/MLflow/K8s wiring, and monitoring
> targets. Intended to be fed to an AI coding assistant (or followed manually) to generate
> the actual code.

---

## 1. Overview and Enterprise Positioning

### 1.1 Why this design exists

The original spec built twelve individual virtual machines, each running a single service,
on a cloud provider that offers all of those as managed services. In a cloud context that
design is indefensible. This specification resolves the tension by choosing the environment
where the design is not merely defensible but mandatory: **an environment where managed
services are not available at all.**

The 12-VM topology, the IP plan, the Terraform/Ansible split, the Jenkins pipeline, and the
Prometheus/Grafana stack all survive. What changes is that the VM-centric, no-managed-
services design stops being a limitation and becomes the entire point.

### 1.2 The enterprise problem

**Unplanned downtime in discrete and process manufacturing, in plants where operational
technology (OT) data cannot cross the plant boundary.**

Industrial control networks are architected on the Purdue model: Level 0-2 (sensors, PLCs,
SCADA) are separated from Level 4-5 (enterprise IT, internet) by a Level 3.5 demilitarised
zone (DMZ). In regulated, defence-adjacent, or risk-averse operators the rule is absolute:
**no outbound connectivity from the OT network.** IEC 62443, the governing security standard
for industrial automation, is built around this zone-and-conduit segmentation model.

This is not paranoia. Stuxnet, Triton, and the Colonial Pipeline incident all shaped operator
policy. Many plants will not permit a cloud agent on the OT side at any price. Every cloud
predictive-maintenance vendor is therefore structurally excluded from these sites.

**Meanwhile the cost of not doing predictive maintenance is enormous.** Unplanned downtime in
automotive manufacturing is routinely cited in the range of tens of thousands of dollars per
minute of stopped line; in continuous process industries a single unplanned shutdown and
restart can run into millions once off-spec product, restart energy, and schedule disruption
are counted.

**Anvil is a complete ML platform that installs inside the plant, on the plant's own
hardware, with no internet connection, ever.**

### 1.3 Why every original design decision now becomes correct

| Original choice | Looked like | Actually is |
|---|---|---|
| 12 discrete VMs, one service each | Wasteful; use containers or managed services | Matches how plant IT actually operates: VMware or Proxmox on plant hardware, clear service boundaries, individually restorable, auditable by people who do not use Kubernetes |
| Self-hosted Postgres on VM08 | Reinventing RDS | There is no RDS. There is a server in a rack in the plant |
| Self-hosted MLflow on VM06 | Reinventing Vertex AI | No outbound connectivity means no SaaS registry, at all |
| Jenkins or Gitea on VM02 | Old-fashioned CI | Air-gapped CI must be self-hosted; GitHub Actions requires the internet |
| Prometheus and Grafana on their own VMs | Over-provisioned | Plant operations already run Grafana on a wall display; this is the native idiom |
| Terraform targeting libvirt (a no-cost-lab option) | The budget compromise | **The correct answer.** Terraform's libvirt provider against Proxmox or bare KVM is exactly right for on-prem |
| Private subnet with no bastion tier | An acknowledged gap | Becomes correct once the whole platform sits behind the OT DMZ; the jump host is the plant's existing one |
| No object storage, local disk artifacts | Not cloud-native | Local NAS is what exists. Cloud-native is irrelevant here |

The original spec was already designing for on-premise. It just had not said so.

### 1.4 Who pays

| Buyer | Their pain | Budget line |
|---|---|---|
| Plant Manager | Unplanned line stops; personally accountable for OEE | Operations budget, and it is large |
| Maintenance Manager | Reactive or fixed-calendar maintenance; over-servicing healthy machines while surprised by failures | Maintenance budget |
| OT Security Manager | Has vetoed every cloud vendor; under pressure to enable analytics anyway | Veto power — must be a champion, not an obstacle |
| CFO | Spare-parts inventory is capital sitting on shelves against unpredictable failures | Working capital |

**The value model, for a single line:**

| Quantity | Value |
|---|---|
| Line output value | €18,000/hour |
| Unplanned downtime events per year | 42 |
| Average duration per event | 3.1 hours |
| Annual unplanned downtime cost | ~€2.34M |
| Realistic reduction from predictive maintenance | 20-30% |
| **Annual value, one line** | **€470k - €700k** |

Secondary savings: **reduced over-maintenance** (condition-based servicing extends intervals
materially), **spare-parts inventory** (predictable failure horizons let you order rather than
stock), and **planned versus emergency labour** (emergency call-out rates are multiples of
planned-window labour cost).

A platform that costs a few hundred thousand to deploy against €500k+ of annual value per
line, in a plant with a dozen lines, is an easy business case. The hard part is not economics;
it is trust (§16).

---

## 2. High-Level Architecture

```
╔══════════ Level 0-2: OT Network — NO OUTBOUND CONNECTIVITY ══════════╗
║                                                                        ║
║   [Sensors] ── [PLCs] ── [SCADA / Historian: PI, Ignition, Wonderware] ║
║                                    │                                   ║
║                                    │ OPC-UA (read-only)                ║
╚════════════════════════════════════│═══════════════════════════════════╝
                                     │  DATA DIODE or strictly one-way
                                     ▼  firewall rule — OT never accepts
╔══════════ Level 3.5: DMZ — ANVIL PLATFORM ═════════════════════════════╗
║                                                                        ║
║  VM01 ctrl-node       10.20.2.10   Ansible control, ops runbooks       ║
║  VM02 gitea-jenkins   10.20.2.11   Git + CI, fully local               ║
║  VM03 k8s-cp          10.20.2.20   Control plane                      ║
║  VM04 k8s-wk1         10.20.2.21   Worker                             ║
║  VM05 k8s-wk2         10.20.2.22   Worker                             ║
║  VM06 mlflow          10.20.2.30   Tracking + registry                ║
║  VM07 ingest          10.20.2.31   OPC-UA client → TimescaleDB        ║
║  VM08 timescale       10.20.2.40   Time-series store                  ║
║  VM09 prometheus      10.20.2.50   Platform metrics                   ║
║  VM10 grafana         10.20.2.51   Operator dashboards + wall display ║
║  VM11 training        10.20.2.60   GPU-optional training host         ║
║  VM12 registry-mirror 10.20.2.61   Offline artifact mirror            ║
║                                                                        ║
║  Serving runs in Kubernetes: inference API, alerting, health scoring   ║
╚═══════════════════════════════════│════════════════════════════════════╝
                                    │  scheduled export, reviewed
                                    ▼  aggregates only — never raw signals
╔══════════ Level 4-5: Enterprise IT ════════════════════════════════════╗
║   CMMS (work orders) · Corporate BI · Multi-plant fleet reporting      ║
╚════════════════════════════════════════════════════════════════════════╝
```

### 2.1 Changes from the original VM plan

| VM | Original | Revised | Reason |
|---|---|---|---|
| VM07 | Optional standalone FastAPI | **OPC-UA ingestion service** | Serving belongs in Kubernetes. Ingestion is the genuinely missing component in the original — there is no data acquisition layer at all |
| VM08 | PostgreSQL | **TimescaleDB** | Still PostgreSQL, plus hypertables, continuous aggregates, and native compression. Sensor data at this volume in vanilla Postgres will not perform, and compression ratios on time-series data materially change the storage budget |
| VM11 | training-env | **training + optional GPU passthrough** | Autoencoders on multivariate windows benefit from a GPU. One consumer-class card in the training host is sufficient |
| VM12 | testing-env | **Offline registry mirror** | The single most critical addition for air-gap. Covered in §11 |

### 2.2 The ingestion path (VM07)

The original spec has no data ingestion design. In an industrial context this is the
component most likely to sink the project, so it is specified precisely:

- **OPC-UA client** subscribing to tags from the plant historian or SCADA layer. OPC-UA is
  the interoperability standard; almost everything modern speaks it.
- **Read-only, one-directional.** The OT network never accepts a connection from the DMZ.
  Where policy demands it, use a hardware data diode — a physically unidirectional link.
  Where a diode is not funded, use strict egress-only firewall rules with no return path
  beyond TCP acknowledgements, and document the residual risk explicitly.
- **Store-and-forward buffering** on VM07, because the historian will be unavailable during
  its own maintenance windows and dropping data during those gaps corrupts training sets in
  ways that are very hard to detect later.
- **Tag mapping as versioned configuration**:
  `PLANT2.LINE3.PUMP7.VIB_AXIAL → machine_id=P7, sensor=vibration_axial, unit=mm/s`.
  This mapping drifts constantly as plant engineers rename tags; treat it as code, version
  it, and alert on unmapped tags rather than silently dropping them.

### 2.3 Key architectural decisions (recorded in `docs/architecture.md`)

- **FastAPI serving runs as a Kubernetes `Deployment` + `Service` + `Ingress` on VM03-05**
  (the serving layer is stateless and benefits from replicas, rolling updates, HPA).
  VM07 is not a serving host — it is the ingestion host.
- **MLflow runs standalone on VM06**, backed by the TimescaleDB instance (database
  `mlflow`); artifact store is local disk/NAS (no object storage exists in an air gap).
- **The model is never baked into the image** — pulled from the MLflow Registry at pod
  startup, so model updates never require a rebuild.
- **Model promotion is a manual approval gate** (Staging automatic, Production manual).

---

## 3. Network Plan

| Item | Value |
|---|---|
| Platform network (DMZ) | `10.20.2.0/24` |
| OT-facing entry | Single egress-only conduit from OT (data diode or one-way firewall rule); no inbound path to OT |
| Enterprise-facing entry | Reviewed, scheduled export of aggregates only; no inbound internet, no public IPs |
| SSH | key-based only; jump host is the plant's existing jump host (no dedicated bastion in the 12-VM budget) |
| Internet | none — see §11 for the update path |

### IP Allocation

| VM | Hostname | IP | Ports |
|---|---|---|---|
| VM01 | ctrl-node | 10.20.2.10 | 22 |
| VM02 | gitea-jenkins | 10.20.2.11 | 22, 3000 (Gitea), 8080 (Jenkins) |
| VM03 | k8s-cp | 10.20.2.20 | 22, 6443, 2379-2380, 10250-10259 |
| VM04 | k8s-wk1 | 10.20.2.21 | 22, 10250, 30000-32767 |
| VM05 | k8s-wk2 | 10.20.2.22 | 22, 10250, 30000-32767 |
| VM06 | mlflow | 10.20.2.30 | 22, 5000 |
| VM07 | ingest | 10.20.2.31 | 22, 4840 (OPC-UA client outbound) |
| VM08 | timescale | 10.20.2.40 | 22, 5432 |
| VM09 | prometheus | 10.20.2.50 | 22, 9090 |
| VM10 | grafana | 10.20.2.51 | 22, 3000 |
| VM11 | training | 10.20.2.60 | 22 |
| VM12 | registry-mirror | 10.20.2.61 | 22, 5001 (Harbor), 3141 (devpi) |

### Security Zones / Firewall Rules

- `sg-mgmt`: 22 from admin IP.
- `sg-dmz-internal`: all traffic within `10.20.2.0/24`.
- `sg-k8s`: 6443/2379-2380/10250-10259/NodePort range, internal only.
- `sg-ot-egress`: VM07 → OT historian, egress-only on OPC-UA, no return path beyond TCP
  acknowledgements. OT never initiates.
- `sg-enterprise-export`: scheduled, reviewed outbound export of aggregates from VM08/VM10
  to enterprise IT only; no inbound rule.
- No `sg-public`. There is no internet exposure.

---

## 4. Repository Structure (file-level)

```
anvil-platform/
├── README.md
├── Makefile
├── .gitignore
│
├── terraform/
│   ├── main.tf                 # libvirt/Proxmox provider, 12 VM definitions
│   ├── variables.tf
│   ├── outputs.tf
│   ├── backend.tf              # local state on VM01 (no remote state service)
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
│   │   ├── 00-mirror.yml          # VM12 offline mirror FIRST — nothing installs without it
│   │   ├── 01-common.yml
│   │   ├── 02-docker.yml
│   │   ├── 03-kubernetes.yml
│   │   ├── 04-mlflow.yml
│   │   ├── 05-timescaledb.yml
│   │   ├── 06-cicd.yml            # Jenkins + Gitea, fully local
│   │   ├── 07-monitoring.yml
│   │   └── 08-ingest.yml          # VM07 OPC-UA client
│   └── roles/
│       ├── mirror/
│       ├── common/
│       ├── docker/
│       ├── k8s-common/
│       ├── k8s-control-plane/
│       ├── k8s-worker/
│       ├── mlflow/
│       ├── timescaledb/
│       ├── cicd/
│       ├── ingest/
│       ├── prometheus/
│       ├── node_exporter/
│       └── grafana/
│
├── docker/
│   ├── fastapi/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── mlflow/
│   │   └── Dockerfile
│   └── training/
│       └── Dockerfile              # pinned Python + libs; GPU-capable base
│
├── kubernetes/
│   ├── namespace.yml               # mlops
│   ├── inference/
│   │   ├── deployment.yml
│   │   ├── service.yml
│   │   ├── configmap.yml           # MLFLOW_TRACKING_URI, MODEL_NAME, MODEL_STAGE
│   │   ├── secret.yml              # DB creds
│   │   └── ingress.yml
│   ├── alerting/
│   │   ├── deployment.yml          # tiered alerting engine + CMMS bridge
│   │   └── service.yml
│   └── hpa.yml                     # autoscale inference API on CPU or request rate
│
├── ml/
│   ├── data/
│   │   ├── raw/                    # exported sensor windows, health-labeled where available
│   │   └── processed/
│   ├── ingest/
│   │   ├── tag_mapping.yml         # versioned OPC-UA tag → machine/sensor/unit mapping
│   │   └── opcua_client.py         # read-only subscriber + store-and-forward buffer
│   ├── notebooks/
│   │   └── 01-eda.ipynb            # vibration spectra, health-score exploration
│   ├── training/
│   │   ├── train.py                # orchestrates layers 1-3, logs to MLflow, registers model
│   │   ├── preprocess.py           # sensor health checks: flatline, drift, gaps, units
│   │   ├── signal.py               # FFT, envelope analysis, BPFO/BPFI/BSF/FTF tracking
│   │   ├── features.py             # windowing, spectral + statistical features
│   │   ├── anomaly.py              # Layer 1: autoencoder/VAE, reconstruction-error health score
│   │   ├── rul.py                  # Layer 2: health-index trajectory + RUL with uncertainty band
│   │   ├── classify.py             # Layer 3: supervised fault classification (multi-class)
│   │   └── config.yml              # hyperparameters, experiment name, bearing geometry table
│   ├── evaluation/
│   │   └── evaluate.py             # precision of alerts vs. work-order outcomes; regression gate
│   └── models/
│       └── .gitkeep                # local scratch only; source of truth is MLflow registry
│
├── api/
│   ├── main.py                     # FastAPI app entrypoint
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── model_loader.py         # loads model from MLflow Registry by name+stage
│   │   ├── schemas.py              # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── predict.py          # POST /predict (sensor window → health/RUL/tier)
│   │   │   ├── alerts.py           # GET /alerts, POST /alerts/{id}/ack
│   │   │   └── health.py
│   │   ├── alerting.py             # tier logic (Watch/Plan/Urgent/Stop) + explanation builder
│   │   ├── cmms.py                 # work-order bridge + technician feedback ingestion
│   │   ├── db.py                   # SQLAlchemy engine/session (TimescaleDB)
│   │   └── metrics.py              # prometheus_fastapi_instrumentator setup
│   └── tests/
│       ├── test_predict.py
│       └── test_health.py
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alert.rules.yml         # platform-health rules (see §9)
│   └── grafana/
│       └── dashboards/
│           ├── node-exporter.json
│           ├── kubernetes-cluster.json
│           ├── inference-api.json
│           ├── model-performance.json
│           ├── sensor-health.json
│           └── operator-line.json  # wall-display dashboard for plant operators
│
├── scripts/
│   ├── bootstrap.sh
│   ├── generate-inventory.py
│   ├── import-update-bundle.sh     # verify signature, import to VM12 mirrors
│   ├── train-and-register.sh       # runs train.py, tags model, promotes stage
│   └── smoke-test.sh               # curl POST /predict with a sample sensor window
│
├── cicd/
│   ├── Jenkinsfile                 # fully offline; Gitea webhook trigger
│   └── stages/
│       ├── test.sh
│       ├── build.sh
│       ├── train.sh
│       ├── evaluate.sh
│       ├── promote.sh
│       ├── deploy.sh
│       └── smoke.sh
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

## 5. The ML Workload — Remaining Useful Life and Anomaly Detection on Rotating Equipment

**Use case: RUL and anomaly detection on pumps, compressors, motors, gearboxes, and their
bearings.** This replaces any tabular business-ML dataset, which makes no sense in a plant.

### 5.1 The data is fundamentally different from tabular churn

Industrial ML fails for reasons that never arise in tabular business ML:

| Property | Churn data | Industrial sensor data |
|---|---|---|
| Volume | ~7,000 rows | 200 sensors × 1 Hz × 24/7 = ~17M points/day/machine |
| Structure | One row per customer | Multivariate time series, irregular sampling, gaps |
| Labels | Every row labelled | **Extremely few.** A given machine may fail twice a year |
| Class balance | ~26% positive | Failures are well under 0.1% of windows |
| Failure modes | One | Many, each with a different signature |
| Consequence of false negative | Lost customer | Destroyed equipment, potentially injured people |
| Consequence of false positive | Wasted email | Unnecessary line stop, costing real production |

**The extreme label scarcity is the defining constraint.** You cannot train a supervised
failure classifier on four labelled failures.

### 5.2 The three-layer model architecture

**Layer 1 — Unsupervised anomaly detection** (works from day one, no labels required):

- Train an autoencoder or a variational autoencoder on windows of sensor data taken from
  known-healthy operating periods.
- Reconstruction error becomes the health score. Healthy data reconstructs well; novel
  behaviour does not.
- Complement with classical signal processing, which is essential and frequently omitted:
  **FFT and envelope analysis of vibration signals.** Bearing defects produce energy at
  characteristic frequencies (BPFO, BPFI, BSF, FTF) computable directly from bearing geometry
  and shaft speed. Tracking amplitude at those specific frequencies is decades-old,
  physics-grounded, and outperforms a naive deep model on small data.

**Layer 2 — Degradation trend modelling** (once you have some failure history):

- Fit health-index trajectories and extrapolate to a failure threshold.
- Output a *distribution* over remaining useful life, not a point estimate. "Failure likely in
  8-21 days, 80% confidence" is actionable for maintenance scheduling; "14.3 days" is false
  precision that destroys trust the first time it is wrong.

**Layer 3 — Supervised fault classification** (only after accumulating labelled events):

- Multi-class over failure modes: bearing wear, misalignment, imbalance, cavitation, looseness.
- Realistically 18-24 months of operation before there is enough labelled data. Plan for it;
  do not promise it at kickoff.

### 5.3 The label acquisition loop

Since labels are the binding constraint, the platform must be *designed to manufacture them*.
Every alert produces a maintenance work order. When the technician closes that work order
they select, from a short structured list on a tablet, what they actually found:

```
[ ] Confirmed — bearing degradation
[ ] Confirmed — misalignment
[ ] Confirmed — lubrication issue
[ ] Confirmed — other: ______
[ ] No fault found
[ ] Not inspected
```

That single form is worth more than any modelling choice in the entire project. It converts
maintenance activity into training data, and it is the reason the system improves over time
rather than plateauing. Integrate it with the plant's existing CMMS (SAP PM, Maximo, Fiix) —
technicians will not use a second system, and asking them to is how these deployments die.

---

## 6. Machine Learning Pipeline (concrete steps → files)

| Pipeline stage | File | Detail |
|---|---|---|
| Data acquisition | `ml/ingest/opcua_client.py` on VM07 | read-only OPC-UA subscriber, tag mapping from `ml/ingest/tag_mapping.yml`, store-and-forward buffer; alert on unmapped tags |
| Data validation | `ml/training/preprocess.py` | sensor health checks — flatline channels, drift, gaps, units; reject corrupt windows before they poison training |
| Signal processing | `ml/training/signal.py` | FFT + envelope analysis; track BPFO/BPFI/BSF/FTF amplitudes from bearing geometry + shaft speed |
| Feature engineering | `ml/training/features.py` | fixed-length windows, spectral + statistical features, health-window selection |
| Train Layer 1 (anomaly) | `ml/training/anomaly.py` via `train.py` | autoencoder/VAE on known-healthy windows; reconstruction-error threshold → health score |
| Train Layer 2 (RUL) | `ml/training/rul.py` via `train.py` | health-index trajectory fit, extrapolation to failure threshold with uncertainty band |
| Train Layer 3 (classify) | `ml/training/classify.py` via `train.py` | multi-class fault classification, enabled only after labelled events accumulate |
| MLflow logging | `train.py` | `mlflow.start_run()`, log params/metrics, `mlflow.log_model()` (pyfunc) with the full run |
| Register model | `train.py` / `scripts/train-and-register.sh` | register as `anvil-health`, transition to `Staging`, manual/automatic promotion to `Production` after evaluation passes |
| Evaluate | `ml/evaluation/evaluate.py` | alert precision vs. work-order outcomes; regression gate vs. current Production model |
| Build Docker image | CI/CD `build.sh` | `docker/fastapi/Dockerfile`, image contains code only — model pulled from MLflow Registry **at container startup** |
| Deploy to Kubernetes | CI/CD `deploy.sh` | `kubectl rollout restart` (re-pulls latest Production model) |
| REST API | `api/app/routers/predict.py` | `POST /predict` (sensor window → health score, tier, RUL, explanation) |
| Alerting | `api/app/alerting.py`, `kubernetes/alerting/` | tier logic + explanation builder + CMMS bridge (§7) |
| Monitoring | `api/app/metrics.py` + Prometheus | request rate/latency, tier distribution, health-score drift (§9) |

---

## 7. Serving and Alerting

### 7.1 FastAPI Model Server — Concrete Contract

```
POST /predict
Request body (example):
{
  "machine_id": "P7",
  "window_start": "2026-08-01T00:00:00Z",
  "sensors": {
    "vibration_axial_mms": [2.1, 2.2, ...],     // 1 Hz × window
    "vibration_radial_mms": [1.8, 1.9, ...],
    "temperature_c": [63.1, 63.2, ...],
    "current_a": [11.2, 11.2, ...]
  },
  "shaft_speed_rpm": 1485
}

Response:
{
  "machine_id": "P7",
  "health_score": 0.82,
  "tier": "plan",
  "rul_days": { "lower": 9, "upper": 24, "confidence": 0.8 },
  "explanation": "Vibration at 142 Hz rose 3.4× over 21 days. ...",
  "model_version": "3",
  "model_stage": "Production"
}
```

- `GET /health` — checks DB connectivity + model loaded; K8s readiness/liveness probe.
- `GET /model-info` — currently loaded model name/version/stage.
- `app/model_loader.py` — on startup,
  `mlflow.pyfunc.load_model(f"models:/anvil-health/{MODEL_STAGE}")` via
  `MLFLOW_TRACKING_URI` from env/ConfigMap; `/reload-model` admin endpoint for promotion
  without pod restart.
- Every prediction is logged to TimescaleDB (`predictions` table) for later analysis and
  drift detection.

### 7.2 Alert tiering

The model output must land in the maintenance workflow, not in a dashboard nobody opens.
Tiering exists because the failure mode of these systems is alert fatigue — once operators
start ignoring alerts the platform is dead regardless of model quality:

| Tier | Condition | Action | Target volume |
|---|---|---|---|
| Watch | Health index degrading, RUL > 30 days | Dashboard only, no notification | Any |
| Plan | RUL 7-30 days, confidence > 70% | CMMS work order at next planned window | ≤ 5/week/line |
| Urgent | RUL < 7 days, or anomaly score critical | Notify maintenance supervisor directly | ≤ 1/week/line |
| Stop | Imminent catastrophic signature | Page + recommend controlled shutdown | ≤ 2/year/line |

Those volume targets are commitments, not estimates. Set thresholds to hit them, then tighten
as precision is empirically demonstrated. A system that generates 40 alerts a week will be
muted within a month, and no amount of model accuracy recovers from that.

**Every alert must carry an explanation** in the operator's language, not the data
scientist's:

> **PUMP-7, drive-end bearing — Plan tier**
> Vibration at 142 Hz has risen 3.4× over 21 days. That frequency corresponds to the
> outer-race defect frequency for this bearing at current shaft speed. Temperature is up
> 6°C over the same period. Similar signatures on PUMP-3 (Mar 2025) and PUMP-11 (Sep 2025)
> preceded bearing failure by 12 and 19 days.
> **Estimated remaining life: 9-24 days (80% confidence).**
> **Recommended: replace drive-end bearing at the next planned stop.**

The reference to prior similar cases is what converts scepticism into trust. Maintenance
technicians have decades of pattern knowledge; showing them the system recognises the same
patterns they do is worth more than any accuracy figure.

---

## 8. Database Schema (TimescaleDB, VM08)

TimescaleDB is PostgreSQL: it keeps the entire original schema and adds hypertables,
continuous aggregates, and native compression — required for 17M points/day/machine.

```sql
-- Sensor telemetry: hypertable, compressed, retention-limited
CREATE TABLE sensor_telemetry (
  time        TIMESTAMPTZ NOT NULL,
  machine_id  VARCHAR(20) NOT NULL,
  sensor      VARCHAR(50) NOT NULL,
  value       DOUBLE PRECISION,
  unit        VARCHAR(10)
);
SELECT create_hypertable('sensor_telemetry', 'time');

-- Continuous aggregate: hourly per-machine stats (feeds dashboards and health scores)
CREATE MATERIALIZED VIEW hourly_stats
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS bucket, machine_id, sensor,
       avg(value) AS avg, stddev(value) AS stddev, max(value) AS max
FROM sensor_telemetry
GROUP BY bucket, machine_id, sensor;

-- Prediction audit log (unchanged in spirit from the original spec)
CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  machine_id VARCHAR(20) NOT NULL,
  input_json JSONB NOT NULL,
  health_score FLOAT,
  tier VARCHAR(10),
  rul_lower_days FLOAT,
  rul_upper_days FLOAT,
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

-- Tiered alerts
CREATE TABLE alerts (
  id SERIAL PRIMARY KEY,
  machine_id VARCHAR(20) NOT NULL,
  tier VARCHAR(10) NOT NULL,
  message JSONB,               -- the explanation object (see §7.2)
  acked_by VARCHAR(50),
  acked_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now()
);

-- Label acquisition loop: work orders + technician feedback (the training-data factory)
CREATE TABLE work_order_feedback (
  id SERIAL PRIMARY KEY,
  alert_id INTEGER REFERENCES alerts(id),
  work_order_id VARCHAR(50),
  machine_id VARCHAR(20) NOT NULL,
  result VARCHAR(30) NOT NULL,  -- confirmed_bearing | confirmed_misalignment |
                                -- confirmed_lubrication | confirmed_other |
                                -- no_fault_found | not_inspected
  detail VARCHAR(500),
  resolved_at TIMESTAMP DEFAULT now()
);
```

**MLflow backend store**: use this same TimescaleDB instance (a separate `mlflow` database)
for MLflow's tracking backend instead of the default SQLite, so experiment history survives
VM06 being rebuilt — `mlflow server --backend-store-uri
postgresql://mlflow:***@10.20.2.40/mlflow --default-artifact-root /opt/mlflow/artifacts`.

**Retention policy**: raw telemetry kept per plant data-retention rules (configurable, with
hourly aggregates kept indefinitely); `predictions` archived rather than dropped so drift
analysis can always look back.

---

## 9. Monitoring — Concrete Targets

**Prometheus scrape configs:**
- `node_exporter` — all 12 VMs, port 9100.
- `kubernetes-nodes/pods/cadvisor` — via `kubernetes_sd_configs`.
- `inference-api` — `/metrics` via `prometheus-fastapi-instrumentator` in `api/app/metrics.py`,
  scraped through the K8s Service.
- `ingest` — VM07: tag ingestion rate, buffer depth, unmapped-tag counter, backlog age
  (an exporter sidecar; ingestion health is platform health).
- `timescale_exporter` — VM08, port 9187 (query/connection counts, hypertable sizes, chunk
  stats for `sensor_telemetry` and `predictions` growth).
- `mlflow` — MLflow does not expose Prometheus metrics natively; front it with a small
  exporter sidecar or rely on `node_exporter` on VM06 + FastAPI/Timescale metrics for the
  ML story (document this limitation).

**Grafana dashboards:**
- Node Exporter Full (ID 1860).
- Kubernetes Cluster (ID 315/7249).
- **Inference API**: request rate, error rate (4xx/5xx), p50/p95/p99 latency for `/predict`.
- **Model Performance**: health-score distribution over time, tier distribution (drift signal
  — a sudden shift in Urgent-tier volume is worth alerting on), alert precision trend vs.
  `work_order_feedback` outcomes (the metric that actually matters), sourced from
  `model_metadata` / MLflow API.
- **Sensor Health**: flatline count, gap count, unmapped tags per machine (a model silently
  trained on a flatlined channel is worse than no model).
- **Operator Line**: wall-display dashboard in the plant's existing Grafana idiom.

**Example alert rules (platform health):**
- `InferenceHighErrorRate` — 5xx rate > 5% over 5m.
- `InferenceHighLatency` — p95 > 500ms over 5m.
- `IngestionStalled` — tag rate near zero on VM07 (upstream integration failure).
- `SensorFlatline` — channel stddev ≈ 0 for > 24h.
- `UnmappedTags` — unmapped-tag counter rising.
- `NoModelLoaded` — `/health` reporting no model loaded for > 2m.
- `RegistryBackupStale` — MLflow registry/NAS backup older than N days (§11.3).

**Model-level alerting** (Watch/Plan/Urgent/Stop) is delivered by the tiered alerting
engine (§7.2), not by Prometheus — Prometheus watches the platform; the engine watches
the machines.

---

## 10. CI/CD Pipeline — Fully Offline

Jenkins on VM02, triggered by Gitea webhooks. **No GitHub Actions**: a self-hosted runner
still phones home to GitHub, and there is no internet. All artifacts push to the local
Harbor mirror on VM12, never to a public registry. Stages, encoded in
`cicd/Jenkinsfile` / `cicd/stages/*`:

1. **Checkout** — Gitea push to `main`, or the retraining schedule.
2. **Test** (`test.sh`) — `pytest api/tests/`.
3. **Build** (`build.sh`) — build and tag the inference image (code-only, model pulled at
   runtime — see §6); push to Harbor on VM12.
4. **Train** (`train.sh`) — runs `ml/training/train.py` on VM11 (GPU-optional); logs to
   MLflow (VM06); proceeds only if `evaluate.py` confirms no regression vs. the current
   Production model (e.g. alert-precision or reconstruction-error tolerance in
   `ml/training/config.yml`).
5. **Register & Promote** (`promote.sh`) — new version to `Staging`; transition to
   `Production` is a Jenkins `input` step (manual approval gate — auditable, realistic).
6. **Deploy** (`deploy.sh`) — `kubectl rollout restart deployment/inference -n mlops` so
   pods reload the latest Production model on startup.
7. **Smoke** (`smoke.sh`) — POST a known sensor window to `/predict`, expect 200 + sane
   health score before the pipeline goes green.

Retraining cadence: model updates are artifacts in the local MLflow registry — they never
require a package or image update. That separation is what keeps the system improvable
inside an air gap.

---

## 11. Air-Gap Operations — the Hardest Part

Everything above is normal engineering. This section is where air-gapped deployments
actually fail, and it is almost never specified in advance.

### 11.1 The offline mirror (VM12)

Nothing can be pulled from the internet. Every dependency must be mirrored inside the plant:

```
VM12 hosts:
  ├── Docker registry (Harbor)      — all container images
  ├── PyPI mirror (devpi/bandersnatchpartial) — Python packages
  ├── APT mirror (aptly)            — OS packages
  ├── Helm chart museum             — charts
  └── Terraform provider mirror     — providers
```

The mirror is provisioned before anything else (`ansible/playbooks/00-mirror.yml`) — no
other role can install a package until it exists.

### 11.2 The update procedure

```
1. On an internet-connected staging machine outside the plant:
   - Pull the required image, package, and provider set at pinned versions
   - Run vulnerability scanning (Trivy) — offline systems do not get automatic patching,
     so scanning at import time is the only gate that exists
   - Export to a signed bundle: anvil-update-2026-08.tar.gz + detached signature

2. Physical transfer on approved removable media, following the plant's media policy —
   which typically includes a scanning kiosk. Budget days for this, not minutes.

3. Inside the plant:
   - Verify signature. Refuse the bundle on mismatch, no exceptions
   - Import to VM12 mirrors
   - Deploy to a staging namespace first
   - Promote to production in an approved maintenance window
```

**Update cadence is monthly at best, quarterly in practice.** Design accordingly:

- Pin every version. Reproducible builds are not aspirational here, they are structural.
- No `latest` tags anywhere. A `latest` tag in an air-gapped environment is a build that
  cannot be reproduced, which means an incident that cannot be diagnosed.
- Keep N-2 versions of every image on the mirror so rollback never requires a physical
  transfer during an incident.
- Track the delta between the plant's installed versions and current upstream, and report
  it, because the security team will ask and "we don't know" is an unacceptable answer.

### 11.3 Backup and recovery

There is no cross-region replication. There is a plant, and things in the plant break.

- Nightly TimescaleDB backups to plant NAS; weekly to removable media held off-site.
- **MLflow artifacts and the model registry are backed up with the same rigour as the
  database.** Losing the registry means losing the ability to reproduce the model currently
  making maintenance decisions.
- **Restore is tested quarterly.** An untested backup is a hypothesis.
- Documented full-rebuild runbook: bare metal to running platform, executed by plant IT
  without vendor assistance. Assume the vendor cannot get on site for 72 hours.

---

## 12. Deployment Workflow (concrete commands)

```bash
# 1. Provision infrastructure (libvirt/Proxmox on plant hardware)
cd terraform
terraform init
terraform apply -auto-approve

# 2. Import the first signed update bundle onto VM12 (verify signature, then import)
cd ../scripts
./import-update-bundle.sh anvil-update-2026-08.tar.gz

# 3. Generate Ansible inventory
python3 generate-inventory.py > ../ansible/inventory/hosts.ini

# 4. Configure everything (mirror first, then services)
cd ../ansible
ansible-playbook -i inventory/hosts.ini site.yml

# 5. Verify MLflow + TimescaleDB
curl http://10.20.2.30:5000/health
psql -h 10.20.2.40 -U mlflow -d mlflow -c '\dt'

# 6. Verify ingestion is live (tag stream from the OT side)
curl http://10.20.2.31:8000/ingest/status   # tag rate, buffer depth, unmapped tags

# 7. Train and register the first model (shadow mode — see §14 phase 15)
cd ../
./scripts/train-and-register.sh

# 8. Deploy the inference + alerting layers to Kubernetes
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

`scripts/bootstrap.sh` wraps steps 1-5; the `Makefile` mirrors every step
(`make provision`, `make import-bundle`, `make inventory`, `make configure`,
`make bootstrap`, `make train`, `make evaluate`, `make promote`, `make test`,
`make build-image`, `make deploy-k8s`, `make smoke`, `make validate`).

---

## 13. Success Metrics

| Metric | Baseline | Target (12 months) |
|---|---|---|
| Unplanned downtime hours per line per year | 130 | < 95 |
| Failures predicted with ≥ 7 days notice | 0% | > 60% |
| False alarm rate (alerts with no fault found) | — | < 25% |
| Alerts acted upon by maintenance | — | > 80% |
| Calendar-based PM tasks converted to condition-based | 0% | > 30% |
| Emergency spare-parts orders | Baseline | −40% |
| Mean time to diagnose after an alert | — | < 2 hours |

The "alerts acted upon" metric is the real health indicator for the deployment. It measures
trust. If it falls, nothing else matters — the model can be excellent and the project is
still failing.

---

## 14. Implementation Plan

| Phase | Deliverable | Days |
|---|---|---|
| 0 | OT security review, data-flow approval, diode/firewall decision | 5 |
| 1 | Terraform on libvirt/Proxmox, 12 VMs provisioned | 4 |
| 2 | Ansible roles, all services configured, idempotent | 5 |
| 3 | Offline mirror (VM12) + first signed update bundle transfer | 4 |
| 4 | OPC-UA ingestion + tag mapping + store-and-forward buffering | 5 |
| 5 | TimescaleDB schema, hypertables, continuous aggregates, retention | 3 |
| 6 | Kubernetes cluster via kubeadm across VM03-05 | 3 |
| 7 | Baseline signal processing: FFT, envelope analysis, bearing frequencies | 4 |
| 8 | Autoencoder anomaly detection + MLflow tracking | 4 |
| 9 | Health index + RUL estimation with uncertainty bands | 4 |
| 10 | Serving API in Kubernetes + tiered alerting engine | 3 |
| 11 | CMMS integration + technician feedback form | 4 |
| 12 | Grafana operator dashboards + wall display | 3 |
| 13 | Jenkins/Gitea CI, fully offline | 3 |
| 14 | Backup, restore drill, full-rebuild runbook | 3 |
| 15 | Shadow mode: alerts generated, not delivered, precision measured | 20 |
| 16 | Go-live on one line, then fleet rollout | 5 |

**Total: ~62 working days**, of which phase 15 is mostly waiting.

**Phase 15 is non-negotiable.** Run the system in shadow mode for a month before a single
alert reaches an operator. Measure precision against reality first. Delivering a false alarm
in week one costs more trust than a hundred correct alerts later will rebuild.

---

## 15. Suggested Build Order (incremental generation)

1. Terraform (network + compute, 12 VMs) → provision infrastructure on the hypervisor.
2. Ansible `mirror` role (VM12) — nothing else can install without it.
3. Ansible `common` + `docker` + `k8s-*` roles → stand up the 3-node Kubernetes cluster.
4. Ansible `timescaledb` role → VM08, create `mlops` and `mlflow` databases + hypertables.
5. Ansible `ingest` role → VM07: OPC-UA client, tag mapping, buffer; confirm a live tag
   stream lands in TimescaleDB.
6. Ansible `mlflow` role → VM06, pointed at the TimescaleDB backend store.
7. `ml/` code (preprocess, signal, features, anomaly, rul, classify, train) → run once
   manually, confirm a model lands in the MLflow Registry.
8. `api/` code (FastAPI + model_loader + alerting + cmms + TimescaleDB logging) +
   `docker/fastapi/Dockerfile`.
9. Kubernetes manifests (`kubernetes/inference/`, `kubernetes/alerting/`) → deploy
   manually once, validate `/predict`.
10. CI/CD (`cicd/`) → automate steps 7-9 going forward; all artifacts to the VM12 mirror.
11. Monitoring (`monitoring/`) + Grafana dashboards (platform + operator wall display).
12. Documentation, written last so it reflects what was actually built.

---

## 16. Honest Risks

**Trust is the binding constraint, not accuracy.** Maintenance technicians have decades of
hard-won pattern knowledge and have been told before that a system would replace their
judgement. Position Anvil as an instrument that extends their reach — like a thermal camera —
not as an oracle that overrules them. Give them the override, log it, and learn from it. Any
deployment that starts by implying the technicians were doing it wrong will fail regardless of
technical merit.

**The first six months produce weak models.** Label scarcity is real, and the unsupervised
layer will have a mediocre false-alarm rate initially. Communicate this at kickoff. A vendor
who promises accurate RUL predictions in month one is either lying or has never done it, and
the plant manager who has been through a failed IIoT project will recognise which.

**Sensor data quality is worse than anyone expects.** Drifting calibration, dead channels
reporting a constant, tags renamed by an engineer without notice, timestamps in three
different zones, historian compression that has already discarded the transients you need.
Budget 30% of the project for data plumbing and validation, and build monitoring for sensor
health as a first-class feature — a model silently trained on a flatlined channel is worse
than no model.

**Air-gap operations are slow, and the slowness is structural.** A dependency update takes
weeks. A production bug that needs a new library version cannot be hotfixed the same day.
Design for this by keeping the runtime dependency surface deliberately small, and by ensuring
that model updates — which are just artifacts in the local registry — never require a package
update. Separating "new model" from "new code" is the mechanism that keeps the system
improvable inside an air gap.

**The OT security manager is the real decision-maker.** They can veto the project
unilaterally and are professionally rewarded for saying no. Engage them in week one, hand
them the data-flow diagram, accept the data diode if they ask for it, and let them define the
update procedure. Converting them from gatekeeper to co-author is the single highest-leverage
move in the entire engagement.

---

## 17. Documentation Deliverables (contents checklist)

- `docs/architecture.md` — component diagram (OT → diode → DMZ → enterprise IT) + the
  decisions in §2.3.
- `docs/ml-pipeline-diagram.md` — sensors → OPC-UA → TimescaleDB → training → registry →
  inference flow (reuse §6), including the manual-approval promotion gate.
- `docs/infrastructure-diagram.md` — VM table + IP plan (reuse §3).
- `docs/deployment-guide.md` — full bootstrap sequence + bundle import + how to trigger a
  retrain via CI/CD.
- `docs/api-documentation.md` — `/predict`, `/health`, `/model-info`, `/alerts`,
  `/alerts/{id}/ack` request/response examples.
- `docs/training-guide.md` — how to add a sensor or machine, retrain locally, and the
  promotion criteria (e.g. "alert precision must not regress by more than 1% vs current
  Production").
- `docs/troubleshooting.md` — ingestion stalls, mirror/signature failures, model load
  failures on pod startup, TimescaleDB connection pool exhaustion, Prometheus scrape target
  down.

---

## 18. Open Decisions to Confirm Before Generating Code

- [ ] Hypervisor + Terraform provider: Proxmox vs bare KVM via the libvirt provider
      (no cloud provider — there is no cloud)?
- [ ] OT data source: which historian/SCADA exposes the OPC-UA server (PI, Ignition,
      Wonderware), and which tags does the security review approve first?
- [ ] Data diode vs strict egress-only firewall for the OT conduit — decision belongs to
      the OT Security Manager, week one?
- [ ] ML framework: PyTorch autoencoder/VAE (GPU on VM11) vs a lighter classical
      alternative for the anomaly layer; Python signal-processing stack (numpy/scipy) for
      Layer 1 classical path?
- [ ] Inference API deployment target: Kubernetes (recommended) vs standalone host?
- [ ] MLflow artifact store: local disk on VM06 vs NAS mount (both are air-gap-safe; NAS
      survives VM06 rebuild)?
- [ ] CI/CD tool: Jenkins vs Gitea Actions (self-hosted runner, fully local — no GitHub
      Actions, which requires internet)?
- [ ] Model promotion: automatic (metrics-gated) vs manual approval gate (recommended)?
- [ ] CMMS integration: SAP PM vs Maximo vs Fiix — which API does the work-order bridge
      target, and what does the plant's maintenance process require?
- [ ] Feedback taxonomy: confirm the structured technician form (§5.3) with the maintenance
      manager before build?
