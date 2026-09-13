# Anvil — Enterprise MLOps Platform for Air-Gapped Industrial Plants

> **On-premise predictive maintenance for manufacturing plants where production data is not 
> permitted to leave the site.**

## Product: Anvil — Predictive Maintenance on Rotating Equipment

Anvil is a complete ML platform that installs inside the plant, on the plant's own hardware, 
with no internet connection, ever. Designed for environments where managed services are not 
available at all — the entire design is mandatory, not optional.

**Target environment**: Plant OT network (Purdue model, IEC 62443) with absolute rule: no outbound 
connectivity from the OT network. Every cloud predictive-maintenance vendor is structurally 
excluded from these sites.

**Cost of not doing predictive maintenance**: Unplanned downtime in automotive manufacturing is 
routinely cited in the range of tens of thousands of dollars per minute of stopped line; in 
continuous process industries a single unplanned shutdown and restart can run into millions.

**Annual value, one line**: €470k - €700k (20-30% reduction from unplanned downtime of ~€2.34M/year).

## Infrastructure Components

### 1. Terraform — Infrastructure as Code
- **What**: Provisions 12 VMs on plant hardware (libvirt/Proxmox)
- **How**: `terraform init`, `terraform apply` provisions network + compute; local state on 
  VM01 (no remote state service); modules for network, security-groups, compute
- **Key files**: `terraform/main.tf`, `terraform/variables.tf`, `terraform/outputs.tf`, 
  `terraform/modules/`
- **Usage**: `terraform init`, `terraform apply -auto-approve`
- **Enterprise justification**: Correct answer for on-premise; matches how plant IT actually 
  operates (VMware/Proxmox); clear service boundaries; individually restorable; auditable by 
  people who do not use Kubernetes

### 2. Ansible — Configuration Management
- **What**: Self-hosted configuration management; all 12 VMs configured from scratch
- **How**: `ansible-playbook -i inventory/hosts.ini site.yml`; roles for mirror, common, 
  docker, k8s-common, k8s-control-plane, k8s-worker, mlflow, timescaledb, cicd, ingest,
  prometheus, node_exporter, grafana
- **Key files**: `ansible/site.yml`, `ansible/playbooks/`, `ansible/roles/`
- **Usage**: `ansible-playbook -i inventory/hosts.ini site.yml`
- **Enterprise justification**: Air-gapped CI must be self-hosted; GitHub Actions requires the 
  internet; same playbook runs against both provider groups; config parity verified, not assumed

### 3. Kubernetes (kubeadm) — Container Orchestration
- **What**: Self-managed K8s cluster (3 control plane + 2 workers)
- **How**: kubeadm initialized on VM03-05; Calico CNI; join workers; identical across both 
  providers; no managed control plane (GKE/EKS/OCI)
- **Key files**: `kubernetes/`, `Makefile` targets
- **Usage**: `kubectl apply -f kubernetes/`, `kubectl rollout restart`
- **Enterprise justification**: The only way to keep the orchestration layer identical across 
  providers; managed control plane is provider-specific by definition

### 4. OPC-UA Ingestion — Data Acquisition
- **What**: OPC-UA client subscribing to tags from plant historian/SCADA
- **How**: Read-only, one-directional; store-and-forward buffering on VM07; tag mapping as 
  versioned configuration; alert on unmapped tags
- **Key files**: `ml/ingest/opcua_client.py`, `ml/ingest/tag_mapping.yml`, `VM07`
- **Usage**: Tag mapping: `PLANT2.LINE3.PUMP7.VIB_AXIAL → machine_id=P7, sensor=vibration_axial, 
  unit=mm/s`
- **Enterprise justification**: The component most likely to sink the project; OT network never 
  accepts a connection from the DMZ; where policy demands it, use a hardware data diode; where 
  a diode is not funded, use strict egress-only firewall rules

### 5. TimescaleDB — Time-Series Store
- **What**: PostgreSQL with hypertables, continuous aggregates, native compression
- **How**: `create_hypertable('sensor_telemetry', 'time')`; materialized views for hourly stats; 
  retention policy configurable
- **Key files**: `sql/` schemas, `VM08`
- **Usage**: Sensor telemetry table with 200 sensors × 1 Hz × 24/7 = ~17M points/day/machine
- **Enterprise justification**: Required for 17M points/day/machine; vanilla PostgreSQL will not 
  perform; compression ratios on time-series data materially change the storage budget

### 6. FastAPI Serving — Model Inference
- **What**: REST API for model inference in Kubernetes
- **How**: FastAPI app with `/predict` endpoint; model loaded from MLflow Registry at pod 
  startup; never baked into image
- **Key files**: `api/main.py`, `api/app/`, `kubernetes/inference/`
- **Usage**: `POST /predict` with sensor window → health score, tier, RUL, explanation
- **Enterprise justification**: Serving runs in Kubernetes; model updates never require a 
  rebuild; pulled from MLflow Registry at pod startup

### 7. MLflow — Tracking + Registry
- **What**: Standalone MLflow on VM06, backed by TimescaleDB
- **How**: `mlflow server --backend-store-uri postgresql://...; artifact store local disk/NAS` 
  (no object storage in air gap)
- **Key files**: `VM06`, `mlflow/` directory
- **Usage**: Experiment tracking, model registry, version staging
- **Enterprise justification**: No outbound connectivity means no SaaS registry, at all; 
  backend store PostgreSQL in same TimescaleDB instance

### 8. CI/CD — Jenkins (Fully Offline)
- **What**: Self-hosted CI/CD; no GitHub Actions (requires internet)
- **How**: Jenkins on VM02; Gitea webhooks; all artifacts push to local Harbor mirror on VM12; 
  never to public registry
- **Key files**: `cicd/Jenkinsfile`, `cicd/stages/`
- **Usage**: Pipeline stages: test → build → train → evaluate → promote → deploy → smoke
- **Enterprise justification**: No `latest` tags anywhere; a `latest` tag in an air-gapped 
  environment is a build that cannot be reproduced

### 9. Monitoring — Prometheus/Grafana
- **What**: Platform metrics and operator dashboards
- **How**: Prometheus scrapes (node_exporter, kubernetes-nodes/pods/cadvisor, inference-api, 
  timescale_exporter, mlflow); Grafana dashboards (node-exporter, kubernetes-cluster, 
  inference-api, model-performance, sensor-health, operator-line)
- **Key files**: `monitoring/prometheus/`, `monitoring/grafana/dashboards/`
- **Usage**: Alert rules (InferenceHighErrorRate, InferenceHighLatency, IngestionStalled, 
  SensorFlatline, UnmappedTags, NoModelLoaded, RegistryBackupStale)
- **Enterprise justification**: Plant operations already run Grafana on a wall display; this 
  is the native idiom

### 11. Air-Gap Operations — Update Procedure
- **What**: How dependencies are updated in air-gapped environment
- **How**: Internet-connected staging machine → pull required images/packages/providers at 
  pinned versions → vulnerability scanning (Trivy) → export to signed bundle → physical 
  transfer on approved removable media → verify signature → import to VM12 mirrors → deploy 
  to staging namespace → promote to production in approved maintenance window
- **Enterprise justification**: Update cadence is monthly at best, quarterly in practice; 
  pin every version; no `latest` tags; keep N-2 versions of every image on the mirror

## Repository Structure

```
anvil-platform/
├── README.md
├── Makefile
├── .gitignore
├── terraform/                  # 12 VM definitions, network, security, compute
├── ansible/                    # playbooks, roles, inventory
├── docker/                     # FastAPI, MLflow, training Dockerfiles
├── kubernetes/                 # namespace, inference, alerting, HPA manifests
├── ml/                         # data, ingest, notebooks, training, evaluation, models
├── api/                        # FastAPI app, routers, schemas, db, metrics, tests
├── monitoring/                 # prometheus, grafana dashboards
├── scripts/                    # bootstrap, inventory, import-update-bundle, train-and-register,
│   smoke-test
├── cicd/                       # Jenkinsfile, stages (test, build, train, evaluate, promote, deploy, smoke)
└── docs/                       # architecture, ml-pipeline-diagram, infrastructure, deployment,
    api-documentation, training-guide, troubleshooting
```

## Deployment Workflow

1. Provision infrastructure (Terraform on libvirt/Proxmox)
2. Import signed update bundle onto VM12
3. Generate Ansible inventory
4. Configure everything (mirror first, then services)
5. Verify MLflow + TimescaleDB
6. Verify ingestion is live
7. Train and register the first model (shadow mode)
8. Deploy inference + alerting layers to Kubernetes
9. Smoke test
10. Verify monitoring

Total: ~62 working days, of which phase 15 (shadow mode) is mostly waiting.

**Phase 15 is non-negotiable**: Run the system in shadow mode for a month before a single 
alert reaches an operator. Measure precision against reality first.