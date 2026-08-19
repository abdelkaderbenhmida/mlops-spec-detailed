# Anvil — Enterprise MLOps Platform for Air-Gapped Industrial Plants

On-premise predictive maintenance for manufacturing plants where production data is not
permitted to leave the site. Anvil installs inside the plant's Level 3.5 DMZ on the plant's
own hardware — 12 VMs, no internet connection, ever.

## The problem it solves

Unplanned downtime in discrete and process manufacturing costs tens of thousands of euros
per minute of stopped line. OT networks (Purdue model, IEC 62443) forbid outbound
connectivity, which structurally excludes every cloud predictive-maintenance vendor. Anvil
is the answer those sites can actually install: a complete ML platform — ingestion, model
registry, serving, alerting, CI/CD — that runs entirely behind the plant boundary.

## What it does

- **Infrastructure as Code** (Terraform): 12 VMs in a private `10.20.2.0/24` DMZ subnet,
  provisioned on the plant's hypervisor (Proxmox/bare KVM via the libvirt provider). No
  public subnet, no NAT, no cloud credentials.
- **Configuration management** (Ansible): offline mirror (VM12) first, then Kubernetes
  cluster (1 control plane + 2 workers), TimescaleDB (telemetry + app DB + MLflow backend),
  MLflow tracking/registry, OPC-UA ingestion (VM07), Gitea + Jenkins, Prometheus + Grafana,
  node_exporter on every VM.
- **Data acquisition**: read-only OPC-UA client on VM07 pulling from the plant
  historian/SCADA through a data diode or strictly one-way firewall rule; store-and-forward
  buffering; versioned tag mapping; unmapped tags are alerted on, never silently dropped.
- **ML pipeline** (RUL + anomaly detection on rotating equipment — pumps, compressors,
  motors, gearboxes): Layer 1 unsupervised autoencoder/VAE anomaly detection plus classical
  FFT/envelope analysis of bearing frequencies (BPFO/BPFI/BSF/FTF), Layer 2 health-index →
  remaining useful life with uncertainty bands, Layer 3 supervised fault classification
  (bearing wear, misalignment, imbalance, cavitation, looseness) once labelled events
  accumulate. Training logs to MLflow and registers `anvil-health`; promotion to `Staging`
  is automatic, to `Production` it is a manual gate.
- **Label acquisition**: every alert creates a CMMS work order; the technician's structured
  close-out ("confirmed bearing degradation / no fault found / …") is fed back as training
  data — the mechanism that makes the system improve over time.
- **Serving** (FastAPI in Kubernetes): `POST /predict` (sensor window → health score, tier,
  RUL distribution, explanation), `GET /health`, `GET /model-info`. The model is pulled from
  the MLflow Model Registry at container startup (never baked into the image). Tiered
  alerting (Watch/Plan/Urgent/Stop) lands in the maintenance workflow with explanations
  operators can trust.
- **Monitoring**: Prometheus scrapes node_exporter (all VMs), inference API, ingestion
  status, and timescale_exporter; Grafana dashboards for node metrics, cluster, inference
  API, model performance, sensor health, and an operator wall display.
- **CI/CD** (Jenkins + Gitea, fully offline): test → train → evaluate → manual promotion
  approval → build → deploy → smoke. All artifacts come from the VM12 mirror — no GitHub,
  no public registries.
- **Air-gap operations**: signed update bundles on approved media, pinned versions, no
  `latest` tags, N-2 image retention on the mirror, nightly NAS backups (MLflow registry
  included), quarterly restore drills, documented full-rebuild runbook.

## Key decisions (see `docs/architecture.md`)

| Decision | Choice |
|---|---|
| Infrastructure provider | Plant hypervisor via Terraform libvirt provider (Proxmox/bare KVM); no cloud |
| Network | DMZ `10.20.2.0/24`; one-way OT conduit; no internet exposure |
| ML problem | RUL + anomaly detection on rotating equipment (3-layer: anomaly → trend → classify) |
| ML framework | Autoencoder/VAE (PyTorch) + classical FFT/envelope analysis (numpy/scipy) |
| Time-series store | TimescaleDB on VM08 (hypertables, continuous aggregates, compression) |
| Ingestion | OPC-UA read-only client on VM07, store-and-forward buffering |
| Inference API location | Kubernetes Deployment on the 3-node cluster |
| MLflow location | Standalone on VM06 (stateful, simplest) |
| Artifact mirror | Harbor + devpi + aptly + chart museum + provider mirror on VM12 |
| CI/CD | Gitea + Jenkins on VM02 (fully offline) |
| Model promotion | Staging automatic, Production manual (approval gate) |
| Alerting | Tiered Watch/Plan/Urgent/Stop with explanations and CMMS integration |

## Repository layout

```
terraform/    hypervisor provisioning, 12 VMs (modules: network, security-groups, compute)
ansible/      Inventory + site.yml + 9 playbooks + 12 roles (mirror first)
docker/       fastapi / mlflow / training images
kubernetes/   mlops namespace, inference + alerting deployments, HPA
ml/           ingest, EDA notebook, signal processing, training (3 layers), evaluation
api/          FastAPI app (model_loader, alerting, cmms, routers, db, metrics)
monitoring/   Prometheus config + alert rules, Grafana dashboards
scripts/      bootstrap, bundle import, inventory generator, train-and-register, smoke test
cicd/         Jenkinsfile + pipeline stages
docs/         Architecture, diagrams, guides, troubleshooting (see docs/)
```

## Quickstart

```bash
# 0. OT security approval of the data-flow diagram (phase-0 gate)

# 1. Provision infrastructure on the plant hypervisor
cd terraform
terraform init
terraform apply -auto-approve

# 2. Import the first signed update bundle (verified, then mirrored)
cd ../scripts
./import-update-bundle.sh anvil-update-2026-08.tar.gz

# 3. Generate Ansible inventory from the IP plan
python3 generate-inventory.py > ../ansible/inventory/hosts.ini

# 4. Configure everything (mirror first)
cd ../ansible
ansible-playbook -i inventory/hosts.ini site.yml

# 5. Verify MLflow + TimescaleDB
curl http://10.20.2.30:5000/health
psql -h 10.20.2.40 -U mlflow -d mlflow -c '\dt'

# 6. Verify the OPC-UA ingestion path
curl http://10.20.2.31:8000/ingest/status

# 7. Train and register the first model (manual promotion gate; shadow mode first)
../scripts/train-and-register.sh

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

`scripts/bootstrap.sh` wraps steps 1-5. A `Makefile` mirrors the same targets.

See `docs/` for architecture diagrams, deployment guide (including the update-bundle
procedure and backups), API documentation, training guide, and troubleshooting.

## Model promotion workflow

```
train.py  →  registers version in MLflow Registry + transitions to Staging
evaluate.py → compares new model against current Production (precision tolerance)
train-and-register.sh --promote  →  manual approval → Production
```

## Verification

```bash
make validate        # py_compile all python, YAML/JSON lint, terraform validate, ansible syntax-check
make train           # run training pipeline end-to-end (needs MLflow reachable)
make smoke           # POST a sample sensor window to /predict
```

## License

Enterprise reference implementation. No warranty.
