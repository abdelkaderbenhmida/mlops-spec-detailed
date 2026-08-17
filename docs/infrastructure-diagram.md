# Infrastructure and IP Plan

Everything below is created by `terraform/` (modules: `network`, `security-groups`,
`compute`) and configured by `ansible/`. Default provider is Google Cloud Platform; the
module boundaries are provider-agnostic enough that swapping providers touches only
`terraform/main.tf` and the compute module.

## Network

| Item | Value |
|---|---|
| VPC / VNet | `10.0.0.0/16` |
| Public subnet | `10.0.1.0/24` — Ingress / load balancer entrypoint only |
| Private subnet | `10.0.2.0/24` — every VM |
| SSH | key-based only; no password auth, root login disabled (`ansible/roles/common`) |
| Egress | NAT gateway for package installs from the private subnet |

There is no dedicated bastion tier in this 12-VM budget. VM01 (`ctrl-node`) doubles as the
jump host: it is the only VM reachable on port 22 from the administrator IP, and it holds
the Terraform state and the Ansible control environment.

## VM allocation

| VM | Hostname | IP | Role | Open ports |
|---|---|---|---|---|
| VM01 | `ctrl-node` | 10.0.2.10 | Terraform + Ansible control node, jump host | 22 |
| VM02 | `git-cicd` | 10.0.2.11 | Jenkins CI/CD | 22, 8080 |
| VM03 | `k8s-cp` | 10.0.2.20 | Kubernetes control plane | 22, 6443, 2379-2380, 10250-10259 |
| VM04 | `k8s-wk1` | 10.0.2.21 | Kubernetes worker | 22, 10250, 30000-32767 |
| VM05 | `k8s-wk2` | 10.0.2.22 | Kubernetes worker | 22, 10250, 30000-32767 |
| VM06 | `mlflow` | 10.0.2.30 | MLflow tracking server + Model Registry | 22, 5000 |
| VM07 | `fastapi` | 10.0.2.31 | Optional Docker build/test host (not in serving path) | 22, 8000 |
| VM08 | `postgres` | 10.0.2.40 | PostgreSQL: `mlops` + `mlflow` databases | 22, 5432 |
| VM09 | `prometheus` | 10.0.2.50 | Prometheus | 22, 9090 |
| VM10 | `grafana` | 10.0.2.51 | Grafana | 22, 3000 |
| VM11 | `training-env` | 10.0.2.60 | Runs `ml/training/*` | 22 |
| VM12 | `testing-env` | 10.0.2.61 | Runs `api/tests/`, load tests | 22 |

`node_exporter` listens on `:9100` on all twelve VMs. `postgres_exporter` listens on `:9187`
on VM08.

## Security groups

| Group | Rule |
|---|---|
| `sg-mgmt` | 22 from the administrator IP only |
| `sg-internal` | all traffic within `10.0.2.0/24` |
| `sg-k8s` | 6443, 2379-2380, 10250-10259 and the NodePort range 30000-32767, internal only |
| `sg-public` | 80/443 from the internet, forwarded to the Ingress NodePort or load balancer |

Defined in `terraform/modules/security-groups/`. No security group allows inbound traffic
from `0.0.0.0/0` except `sg-public` on 80/443.

## Terraform layout

```
terraform/
├── main.tf                    wires the three modules together, 12 VM definitions
├── variables.tf               project id, region, zone, machine types, admin CIDR
├── outputs.tf                 VM names + private IPs (consumed by generate-inventory.py)
├── backend.tf                 remote state backend
├── terraform.tfvars.example   copy to terraform.tfvars and fill in
└── modules/
    ├── network/               VPC, public + private subnets, NAT
    ├── security-groups/       the four rule sets above
    └── compute/               reusable VM resource (name, ip, machine type, tags)
```

`terraform/outputs.tf` emits the hostname → IP mapping that
`scripts/generate-inventory.py` turns into `ansible/inventory/hosts.ini`, so the IP plan is
defined once and never hand-copied.

## Ansible layout

`ansible/site.yml` runs the seven playbooks in order:

| Playbook | Targets | Roles |
|---|---|---|
| `01-common.yml` | all | `common` — base packages, timezone, UFW, SSH hardening |
| `02-docker.yml` | k8s nodes, mlflow, cicd, training | `docker` |
| `03-kubernetes.yml` | VM03-05 | `k8s-common`, `k8s-control-plane`, `k8s-worker` |
| `04-mlflow.yml` | VM06 | `mlflow` |
| `05-postgresql.yml` | VM08 | `postgresql` — creates `mlops` and `mlflow` databases |
| `06-cicd.yml` | VM02 | `cicd` — Jenkins |
| `07-monitoring.yml` | VM09, VM10, all | `prometheus`, `grafana`, `node_exporter` |

Group variables live in `ansible/inventory/group_vars/{all,k8s,mlflow}.yml`. Credentials are
never committed — see [`deployment-guide.md`](deployment-guide.md#secrets).

## Sizing notes

The defaults in `terraform/variables.tf` are lab-sized. For a real workload the two places
that need attention first are the Kubernetes workers (VM04/VM05 — they carry the FastAPI
replicas plus whatever the HPA adds) and VM08, whose `predictions` table grows with every
request and needs a disk sized against expected request volume plus a retention policy.
