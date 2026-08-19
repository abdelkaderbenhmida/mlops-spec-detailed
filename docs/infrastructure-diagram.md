# Infrastructure and IP Plan

Everything below is created by `terraform/` (modules: `network`, `security-groups`,
`compute`) and configured by `ansible/`. The provider is **libvirt against Proxmox or bare
KVM on plant hardware** — there is no cloud provider, no public subnet, and no internet
connectivity. This is deliberate: the platform installs inside the plant's Level 3.5 DMZ,
where managed services do not exist.

## Network

| Item | Value |
|---|---|
| Platform network (DMZ) | `10.20.2.0/24` — every VM |
| Public subnet | none — no internet-facing element exists |
| OT conduit | `sg-ot-egress`: VM07 → OT historian, egress-only OPC-UA, no return path beyond TCP acknowledgements (or hardware data diode where policy demands it) |
| Enterprise export | scheduled, reviewed outbound export of aggregates only; no inbound rule |
| SSH | key-based only; no password auth, root login disabled (`ansible/roles/common`) |
| Egress | none — no NAT gateway; all packages come from the offline mirror on VM12 |

There is no dedicated bastion tier in this 12-VM budget, and there is no public IP to
reach. Access is via the plant's existing jump host. VM01 (`ctrl-node`) holds the Terraform
state (local backend — there is no remote state service in an air gap) and the Ansible
control environment.

## VM allocation

| VM | Hostname | IP | Role | Open ports |
|---|---|---|---|---|
| VM01 | `ctrl-node` | 10.20.2.10 | Terraform + Ansible control node, ops runbooks | 22 |
| VM02 | `gitea-jenkins` | 10.20.2.11 | Gitea (git) + Jenkins CI/CD, fully local | 22, 3000, 8080 |
| VM03 | `k8s-cp` | 10.20.2.20 | Kubernetes control plane | 22, 6443, 2379-2380, 10250-10259 |
| VM04 | `k8s-wk1` | 10.20.2.21 | Kubernetes worker | 22, 10250, 30000-32767 |
| VM05 | `k8s-wk2` | 10.20.2.22 | Kubernetes worker | 22, 10250, 30000-32767 |
| VM06 | `mlflow` | 10.20.2.30 | MLflow tracking server + Model Registry | 22, 5000 |
| VM07 | `ingest` | 10.20.2.31 | OPC-UA client → TimescaleDB, store-and-forward buffer | 22, 4840 (outbound) |
| VM08 | `timescale` | 10.20.2.40 | TimescaleDB: telemetry + `mlops` + `mlflow` databases | 22, 5432 |
| VM09 | `prometheus` | 10.20.2.50 | Prometheus | 22, 9090 |
| VM10 | `grafana` | 10.20.2.51 | Grafana (operator dashboards + wall display) | 22, 3000 |
| VM11 | `training` | 10.20.2.60 | Training host, GPU-optional passthrough | 22 |
| VM12 | `registry-mirror` | 10.20.2.61 | Offline mirror: Harbor, devpi, aptly, Helm chart museum, Terraform provider mirror | 22, 5001, 3141 |

`node_exporter` listens on `:9100` on all twelve VMs. `timescale_exporter` listens on
`:9187` on VM08. An ingestion exporter (tag rate, buffer depth, unmapped tags) runs on VM07.

## Security zones

| Group | Rule |
|---|---|
| `sg-mgmt` | 22 from the administrator IP only |
| `sg-dmz-internal` | all traffic within `10.20.2.0/24` |
| `sg-k8s` | 6443, 2379-2380, 10250-10259 and the NodePort range 30000-32767, internal only |
| `sg-ot-egress` | VM07 → OT historian on OPC-UA; egress-only, OT never initiates |
| `sg-enterprise-export` | scheduled reviewed export of aggregates from VM08/VM10 to enterprise IT |

Defined in `terraform/modules/security-groups/`. No security group allows inbound traffic
from any external network; the only conduits are the one-way OT data path and the reviewed
aggregate export.

## Terraform layout

```
terraform/
├── main.tf                    wires the three modules together, 12 VM definitions
├── variables.tf               hypervisor endpoint, machine types, admin CIDR, GPU passthrough flag
├── outputs.tf                 VM names + private IPs (consumed by generate-inventory.py)
├── backend.tf                 local state on VM01 (no remote state service in an air gap)
├── terraform.tfvars.example   copy to terraform.tfvars and fill in
└── modules/
    ├── network/               DMZ network, security-zone wiring (no VPC, no NAT, no public subnet)
    ├── security-groups/       the five rule sets above
    └── compute/               reusable VM resource (name, ip, machine type, tags)
```

Provider is `terraform-provider-libvirt` against Proxmox or bare KVM — the §"local/libvirt
for a no-cost lab" option from the original spec, now the production answer. Provider
versions come from the mirror on VM12.

`terraform/outputs.tf` emits the hostname → IP mapping that
`scripts/generate-inventory.py` turns into `ansible/inventory/hosts.ini`, so the IP plan is
defined once and never hand-copied.

## Ansible layout

`ansible/site.yml` runs the playbooks in order — the mirror **must** run first, because no
other role can install a package until VM12 serves it:

| Playbook | Targets | Roles |
|---|---|---|
| `00-mirror.yml` | VM12 | `mirror` — Harbor, devpi, aptly, chart museum, provider mirror |
| `01-common.yml` | all | `common` — base packages (from mirror), timezone, UFW, SSH hardening |
| `02-docker.yml` | k8s nodes, mlflow, cicd, training, ingest | `docker` |
| `03-kubernetes.yml` | VM03-05 | `k8s-common`, `k8s-control-plane`, `k8s-worker` |
| `04-mlflow.yml` | VM06 | `mlflow` |
| `05-timescaledb.yml` | VM08 | `timescaledb` — creates `mlops` and `mlflow` databases, hypertables, continuous aggregates, retention |
| `06-cicd.yml` | VM02 | `cicd` — Gitea + Jenkins |
| `07-monitoring.yml` | VM09, VM10, all | `prometheus`, `grafana`, `node_exporter` |
| `08-ingest.yml` | VM07 | `ingest` — OPC-UA client, tag mapping, store-and-forward buffer |

Group variables live in `ansible/inventory/group_vars/{all,k8s,mlflow}.yml`. Credentials are
never committed — see [`deployment-guide.md`](deployment-guide.md#secrets).

## Sizing notes

The defaults in `terraform/variables.tf` are lab-sized. For a real workload the two places
that need attention first are the Kubernetes workers (VM04/VM05 — they carry the inference
replicas plus the alerting engine and whatever the HPA adds) and VM08, whose
`sensor_telemetry` hypertable grows by ~17M points/day/machine and needs a disk sized
against the plant's sensor count, compression ratios, and retention policy. VM11 benefits
from one consumer-class GPU for the autoencoder training. VM12 needs enough disk to hold
N-2 versions of every image and package set.
