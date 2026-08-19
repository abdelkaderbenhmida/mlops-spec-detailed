# Enterprise Upgrade — From "12 VMs in a Lab" to an Air-Gapped Industrial ML Platform

> Target product name: **Anvil** — on-premise predictive maintenance for manufacturing plants
> where production data is not permitted to leave the site.
>
> This document rewrites `mlops-platform-spec-detailed.md`. The 12-VM topology, the IP plan,
> the Terraform/Ansible split, the Jenkins pipeline, and the Prometheus/Grafana stack all
> survive. What changes is that the VM-centric, no-managed-services design stops being a
> limitation and becomes the entire point.

---

## 1. The tension in the original spec

The original is the most implementation-ready of the four documents. It has a real IP
allocation table, security group definitions, file-level repository layout, concrete port
assignments, and a §13 listing open decisions before code generation — which is genuinely
good engineering discipline.

Its unresolved tension is that it builds twelve individual virtual machines, each running a
single service (one VM for Prometheus, one for Grafana, one for Postgres, one for MLflow), on
a cloud provider that offers all of those as managed services. In a cloud context that design
is indefensible: you are paying for the operational burden of self-management while sitting
next to a managed alternative, and §13 even leaves the cloud provider as an open question with
"local/libvirt for a no-cost lab" as an option.

Resolve the tension by choosing the environment where this design is not merely defensible but
mandatory: **an environment where managed services are not available at all.**

---

## 2. The enterprise problem

**Unplanned downtime in discrete and process manufacturing, in plants where operational
technology data cannot cross the plant boundary.**

Industrial control networks are architected on the Purdue model, a layered reference
architecture where Level 0-2 (sensors, PLCs, SCADA) are separated from Level 4-5 (enterprise
IT, internet) by a Level 3.5 demilitarised zone. In regulated, defence-adjacent, or simply
risk-averse operators, the rule is absolute: **no outbound connectivity from the OT network.**
IEC 62443, the governing security standard for industrial automation, is built around this
zone-and-conduit segmentation model.

This is not paranoia. Stuxnet, Triton, and the Colonial Pipeline incident all shaped operator
policy. Many plants will not permit a cloud agent on the OT side at any price, and the
insurance and regulatory consequences of an OT breach are severe enough that "we'll VPN the
sensor data to a cloud ML service" is a conversation that ends immediately.

So every cloud predictive-maintenance vendor is structurally excluded from these sites.

**Meanwhile the cost of not doing predictive maintenance is enormous.** Unplanned downtime in
automotive manufacturing is routinely cited in the range of tens of thousands of dollars per
minute of stopped line; in continuous process industries a single unplanned shutdown and
restart can run into millions once off-spec product, restart energy, and schedule disruption
are counted.

**Anvil is a complete ML platform that installs inside the plant, on the plant's own hardware,
with no internet connection, ever.**

---

## 3. Why every original design decision now becomes correct

| Original choice | Looked like | Actually is |
|---|---|---|
| 12 discrete VMs, one service each | Wasteful; use containers or managed services | Matches how plant IT actually operates: VMware or Proxmox on plant hardware, clear service boundaries, individually restorable, auditable by people who do not use Kubernetes |
| Self-hosted Postgres on VM08 | Reinventing RDS | There is no RDS. There is a server in a rack in the plant |
| Self-hosted MLflow on VM06 | Reinventing Vertex AI | No outbound connectivity means no SaaS registry, at all |
| Jenkins or Gitea on VM02 | Old-fashioned CI | Air-gapped CI must be self-hosted; GitHub Actions requires the internet |
| Prometheus and Grafana on their own VMs | Over-provisioned | Plant operations already run Grafana on a wall display; this is the native idiom |
| Terraform targeting libvirt (the §13 option) | The budget compromise | **The correct answer.** Terraform's libvirt provider against Proxmox or bare KVM is exactly right for on-prem |
| Private subnet with no bastion tier | An acknowledged gap | Becomes correct once the whole platform sits behind the OT DMZ; the jump host is the plant's existing one |
| No object storage, local disk artifacts | Not cloud-native | Local NAS is what exists. Cloud-native is irrelevant here |

The original spec was already designing for on-premise. It just had not said so.

---

## 4. Who pays

| Buyer | Their pain | Budget line |
|---|---|---|
| Plant Manager | Unplanned line stops; they are personally accountable for OEE | Operations budget, and it is large |
| Maintenance Manager | Running reactive or fixed-calendar maintenance; over-servicing healthy machines while surprised by failures | Maintenance budget |
| OT Security Manager | Has vetoed every cloud vendor; is under pressure to enable analytics anyway | Veto power — must be a champion, not an obstacle |
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

Secondary savings that the maintenance manager will raise unprompted:

- **Reduced over-maintenance.** Calendar-based servicing replaces healthy components. Moving
  to condition-based servicing typically extends intervals materially.
- **Spare-parts inventory.** Predictable failure horizons let you order rather than stock,
  releasing working capital.
- **Planned versus emergency labour.** Emergency call-out rates and overtime are multiples of
  planned-window labour cost.

A platform that costs a few hundred thousand to deploy against €500k+ of annual value per
line, in a plant with a dozen lines, is an easy business case. The hard part is not economics;
it is trust, which §11 addresses.

---

## 5. The ML workload, made real

Replace the churn dataset — which makes no sense in a plant — with the actual problem.

**Use case: remaining useful life (RUL) and anomaly detection on rotating equipment** —
pumps, compressors, motors, gearboxes, and their bearings.

### 5.1 The data is fundamentally different from tabular churn

This is the most important technical section, because industrial ML fails for reasons that
never arise in tabular business ML:

| Property | Churn data | Industrial sensor data |
|---|---|---|
| Volume | ~7,000 rows | 200 sensors × 1 Hz × 24/7 = ~17M points/day/machine |
| Structure | One row per customer | Multivariate time series, irregular sampling, gaps |
| Labels | Every row labelled | **Extremely few.** A given machine may fail twice a year |
| Class balance | ~26% positive | Failures are well under 0.1% of windows |
| Failure modes | One | Many, each with a different signature |
| Consequence of false negative | Lost customer | Destroyed equipment, potentially injured people |
| Consequence of false positive | Wasted email | Unnecessary line stop, costing real production |

**The extreme label scarcity is the defining constraint** and it drives the entire modelling
approach. You cannot train a supervised failure classifier on four labelled failures.

### 5.2 The three-layer model architecture

Layer 1 — **Unsupervised anomaly detection** (works from day one, no labels required):

- Train an autoencoder or a variational autoencoder on windows of sensor data taken from
  known-healthy operating periods.
- Reconstruction error becomes the health score. Healthy data reconstructs well; novel
  behaviour does not.
- Complement with classical signal processing, which is essential and frequently omitted:
  **FFT and envelope analysis of vibration signals.** Bearing defects produce energy at
  characteristic frequencies (BPFO, BPFI, BSF, FTF) computable directly from bearing geometry
  and shaft speed. Tracking amplitude at those specific frequencies is decades-old, physics-
  grounded, and outperforms a naive deep model on small data.

Layer 2 — **Degradation trend modelling** (once you have some failure history):

- Fit health-index trajectories and extrapolate to a failure threshold.
- Output a *distribution* over remaining useful life, not a point estimate. "Failure likely in
  8-21 days, 80% confidence" is actionable for maintenance scheduling; "14.3 days" is false
  precision that destroys trust the first time it is wrong.

Layer 3 — **Supervised fault classification** (only after accumulating labelled events):

- Multi-class over failure modes: bearing wear, misalignment, imbalance, cavitation, looseness.
- Realistically 18-24 months of operation before there is enough labelled data. Plan for it;
  do not promise it at kickoff.

### 5.3 The label acquisition loop

Since labels are the binding constraint, the platform must be *designed to manufacture them*.
Every alert produces a maintenance work order. When the technician closes that work order they
select, from a short structured list on a tablet, what they actually found:

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

## 6. Revised architecture

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
║  VM08 timescale       10.20.2.40   Time-series store (was: postgres)  ║
║  VM09 prometheus      10.20.2.50   Platform metrics                   ║
║  VM10 grafana         10.20.2.51   Operator dashboards + wall display ║
║  VM11 training        10.20.2.60   GPU-optional training host         ║
║  VM12 registry-mirror 10.20.2.61   Offline artifact mirror (was: test)║
║                                                                        ║
║  Serving runs in Kubernetes: inference API, alerting, health scoring   ║
╚═══════════════════════════════════│════════════════════════════════════╝
                                    │  scheduled export, reviewed
                                    ▼  aggregates only — never raw signals
╔══════════ Level 4-5: Enterprise IT ════════════════════════════════════╗
║   CMMS (work orders) · Corporate BI · Multi-plant fleet reporting      ║
╚════════════════════════════════════════════════════════════════════════╝
```

### Changes from the original VM plan

| VM | Original | Revised | Reason |
|---|---|---|---|
| VM07 | Optional standalone FastAPI | **OPC-UA ingestion service** | Serving belongs in Kubernetes. Ingestion is the genuinely missing component in the original — there is no data acquisition layer at all |
| VM08 | PostgreSQL | **TimescaleDB** | Still PostgreSQL, plus hypertables, continuous aggregates, and native compression. Sensor data at this volume in vanilla Postgres will not perform, and compression ratios on time-series data materially change the storage budget |
| VM11 | training-env | **training + optional GPU passthrough** | Autoencoders on multivariate windows benefit from a GPU. One consumer-class card in the training host is sufficient |
| VM12 | testing-env | **Offline registry mirror** | The single most critical addition for air-gap. Covered in §7 |

### The ingestion path

The original spec has no data ingestion design. In an industrial context this is the component
most likely to sink the project, so it needs to be specified precisely:

- **OPC-UA client** subscribing to tags from the plant historian or SCADA layer. OPC-UA is the
  interoperability standard; almost everything modern speaks it.
- **Read-only, one-directional.** The OT network never accepts a connection from the DMZ.
  Where policy demands it, use a hardware data diode — a physically unidirectional link.
  Where a diode is not funded, use strict egress-only firewall rules with no return path
  beyond TCP acknowledgements, and document the residual risk explicitly.
- **Store-and-forward buffering** on VM07, because the historian will be unavailable during
  its own maintenance windows and dropping data during those gaps corrupts training sets in
  ways that are very hard to detect later.
- **Tag mapping as versioned configuration**: `PLANT2.LINE3.PUMP7.VIB_AXIAL → machine_id=P7,
  sensor=vibration_axial, unit=mm/s`. This mapping drifts constantly as plant engineers rename
  tags; treat it as code, version it, and alert on unmapped tags rather than silently dropping
  them.

---

## 7. Air-gap operations — the hardest part

Everything above is normal engineering. This section is where air-gapped deployments actually
fail, and it is almost never specified in advance.

### 7.1 The offline mirror (VM12)

Nothing can be pulled from the internet. Every dependency must be mirrored inside the plant:

```
VM12 hosts:
  ├── Docker registry (Harbor)      — all container images
  ├── PyPI mirror (devpi/bandersnatchpartial) — Python packages
  ├── APT mirror (aptly)            — OS packages
  ├── Helm chart museum             — charts
  └── Terraform provider mirror     — providers
```

### 7.2 The update procedure

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
- Track the delta between the plant's installed versions and current upstream, and report it,
  because the security team will ask and "we don't know" is an unacceptable answer.

### 7.3 Backup and recovery

There is no cross-region replication. There is a plant, and things in the plant break.

- Nightly TimescaleDB backups to plant NAS; weekly to removable media held off-site.
- **MLflow artifacts and the model registry are backed up with the same rigour as the
  database.** Losing the registry means losing the ability to reproduce the model currently
  making maintenance decisions.
- **Restore is tested quarterly.** An untested backup is a hypothesis.
- Documented full-rebuild runbook: bare metal to running platform, executed by plant IT
  without vendor assistance. Assume the vendor cannot get on site for 72 hours.

---

## 8. Serving and alerting

The model output must land in the maintenance workflow, not in a dashboard nobody opens.

**Alert tiering**, because the failure mode of these systems is alert fatigue, and once
operators start ignoring alerts the platform is dead regardless of model quality:

| Tier | Condition | Action | Target volume |
|---|---|---|---|
| Watch | Health index degrading, RUL > 30 days | Dashboard only, no notification | Any |
| Plan | RUL 7-30 days, confidence > 70% | CMMS work order at next planned window | ≤ 5/week/line |
| Urgent | RUL < 7 days, or anomaly score critical | Notify maintenance supervisor directly | ≤ 1/week/line |
| Stop | Imminent catastrophic signature | Page + recommend controlled shutdown | ≤ 2/year/line |

Those volume targets are commitments, not estimates. Set thresholds to hit them, then tighten
as precision is empirically demonstrated. A system that generates 40 alerts a week will be
muted within a month, and no amount of model accuracy recovers from that.

**Every alert must carry an explanation** in the operator's language, not the data scientist's:

> **PUMP-7, drive-end bearing — Plan tier**
> Vibration at 142 Hz has risen 3.4× over 21 days. That frequency corresponds to the outer-race
> defect frequency for this bearing at current shaft speed. Temperature is up 6°C over the same
> period. Similar signatures on PUMP-3 (Mar 2025) and PUMP-11 (Sep 2025) preceded bearing
> failure by 12 and 19 days.
> **Estimated remaining life: 9-24 days (80% confidence).**
> **Recommended: replace drive-end bearing at the next planned stop.**

The reference to prior similar cases is what converts scepticism into trust. Maintenance
technicians have decades of pattern knowledge; showing them the system recognises the same
patterns they do is worth more than any accuracy figure.

---

## 9. Success metrics

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
trust. If it falls, nothing else matters — the model can be excellent and the project is still
failing.

---

## 10. Implementation plan

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

## 11. Honest risks

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

**The OT security manager is the real decision-maker.** They can veto the project unilaterally
and are professionally rewarded for saying no. Engage them in week one, hand them the
data-flow diagram, accept the data diode if they ask for it, and let them define the update
procedure. Converting them from gatekeeper to co-author is the single highest-leverage move
in the entire engagement.
