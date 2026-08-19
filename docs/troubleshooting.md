# Troubleshooting

Failure modes this platform actually produces, in rough order of how often they bite.

---

## Pod starts but `/health` says `model_loaded: false`

`api/app/model_loader.py` deliberately catches every exception during load so the process
stays up and reports its state instead of crash-looping. The real error is in the pod log:

```bash
kubectl logs -n mlops deployment/inference | grep -i "Failed to load model"
```

Common causes:

| Symptom in the log | Cause | Fix |
|---|---|---|
| `RESOURCE_DOES_NOT_EXIST: Registered Model with name=anvil-health not found` | Nothing has been trained yet | `./scripts/train-and-register.sh --promote` |
| `No versions ... with stage Production` | A version exists but only in `Staging` | Promote it — `make promote` |
| `Connection refused` / `Max retries exceeded` on port 5000 | MLflow on VM06 is down, or `MLFLOW_TRACKING_URI` is wrong | `curl http://10.20.2.30:5000/health`; check `kubernetes/inference/configmap.yml` |
| `PermissionError` on the artifact path | Artifact store permissions (see below) | fix ownership on VM06 |
| `ModuleNotFoundError` for a library or a version mismatch | Training image and serving image disagree on library versions | pin the same versions in `docker/training/Dockerfile` and `api/requirements.txt` — and note that fixing this requires an update bundle (§"Import failures" below) |

Note that the pod stays `Running` in all these cases. If the readiness probe is configured
to require `status == "healthy"`, the pod will correctly stay out of the Service and no
traffic is served by a model-less replica.

---

## MLflow artifact store permission errors

Symptom during `train.py`:

```
PermissionError: [Errno 13] Permission denied: '/opt/mlflow/artifacts/...'
```

The MLflow server writes artifacts as its own service user; a training job connecting from
VM11 uploads through the server, but a *local* file-scheme artifact root makes the client
try to write the path directly.

- Confirm `--default-artifact-root` is a path the MLflow service user owns:
  `sudo chown -R mlflow:mlflow /opt/mlflow/artifacts`
- Confirm the training host is not configured with a `file:` artifact root pointing at a
  directory that only exists on VM06. Use the MLflow server URL as the root, or mount the
  plant NAS path consistently on both hosts. (Object storage such as S3/GCS does not exist
  in an air-gapped plant — do not follow generic MLflow docs that assume it.)
- After changing ownership, restart the service: `sudo systemctl restart mlflow`.

---

## Model loads locally but not in the pod

Almost always DNS or network policy, not MLflow:

```bash
kubectl run -n mlops nettest --rm -it --image=<image-from-VM12-mirror> -- \
  curl -s http://10.20.2.30:5000/health
```

If that fails, the cluster nodes cannot reach VM06 — check `sg-dmz-internal` covers the pod
CIDR, not just the node subnet.

---

## Promotion took effect in MLflow but the API still serves the old version

Expected. The model is loaded once, in the FastAPI `lifespan` startup hook. Nothing polls
the registry.

```bash
kubectl rollout restart deployment/inference -n mlops
kubectl rollout status deployment/inference -n mlops
curl http://api.mlops.local/model-info   # confirm the new version
```

`cicd/stages/deploy.sh` does this automatically; it is only a surprise when someone promotes
by hand.

---

## Ingestion is stalled or dropping tags

The OPC-UA path (OT → VM07 → TimescaleDB) is the platform's lifeline. Check
`http://10.20.2.31:8000/ingest/status`:

| Reading | Meaning | Fix |
|---|---|---|
| `tag_rate` near zero | OPC-UA subscription died, or the historian is down (possibly its own maintenance window) | check the store-and-forward buffer is accumulating; confirm the egress rule `sg-ot-egress` still exists after any firewall change; contact OT for the historian window |
| `buffer_depth` rising | downstream (TimescaleDB) is slow or down | check VM08 health and the `timescale_exporter` scrape; the buffer is designed for this — do not restart VM07 and lose it |
| `unmapped_tags` rising | plant engineers renamed tags without notice | update `ml/ingest/tag_mapping.yml` (versioned, reviewed, redeployed) — never silently drop the tags |
| flatline count rising | dead channel or sensor fault | a model silently trained on a flatlined channel is worse than no model; alert on it (`SensorFlatline`) and exclude the channel until fixed |

---

## Update bundle import fails

Air-gap imports are deliberately strict:

- **Signature mismatch** — the bundle is refused, no exceptions. Re-request the bundle from
  the staging machine; do not attempt to bypass verification.
- **Disk full on VM12** — the mirror holds N-2 versions of every image and package set;
  prune oldest versions, then re-import.
- **Import succeeded but `apt install` still fails** — check the APT sources point at
  `http://10.20.2.61:3142` (or the aptly path) on every host, not at the public
  repositories. Same for PyPI (`devpi`) and the Docker daemon (`insecure-registries` for
  `10.20.2.61:5001`).
- **A new dependency version is required by a hotfix** — this cannot happen the same day:
  it needs a new signed bundle. This is structural (§"Air-gap operations" in the main
  spec). Keep the runtime dependency surface deliberately small; model updates never
  require a package update.

---

## PostgreSQL / TimescaleDB connection pool exhaustion

Symptom: `/predict` still returns `200` but the logs fill with

```
Failed to log prediction to DB: QueuePool limit of size 5 overflow 10 reached
```

Predictions are still correct — the audit write is best-effort — but the history has holes.

- The engine is configured in `api/app/db.py` with `pool_size=5, max_overflow=10`, so each
  replica can hold up to 15 connections. Multiply by the replica count *and* by the HPA
  maximum before comparing against TimescaleDB's `max_connections` (default 100).
- Fixes, in order of preference: lower the HPA maximum, raise `max_connections` on VM08, or
  put PgBouncer in front of VM08.
- Check current usage: `psql -h 10.20.2.40 -U mlops_app -d mlops -c "SELECT count(*) FROM pg_stat_activity;"`
- `pool_pre_ping=True` and `pool_recycle=3600` are already set, so stale connections after
  a TimescaleDB restart are not the cause.

---

## `sensor_telemetry` / `predictions` table growth

Every request inserts a `predictions` row with a JSONB payload, and every machine produces
~17M telemetry points/day at 1 Hz. These are the fastest growing things in the platform;
`timescale_exporter` on VM08 exposes table/hypertable size for exactly this reason.

```sql
SELECT pg_size_pretty(pg_total_relation_size('sensor_telemetry'));
```

The `sensor_telemetry` hypertable uses native compression (materially changes the storage
budget) and a retention policy set per the plant's data-retention rules — the hourly
continuous aggregate (`hourly_stats`) is kept indefinitely. `predictions` is archived rather
than dropped so drift analysis can always look back. There is no retention policy committed
to the repo by design — the right window depends on plant policy and how far back drift
analysis needs to look.

---

## Prometheus scrape target down

Check `http://10.20.2.50:9090/targets` first, then match the target:

| Target | Check |
|---|---|
| `node_exporter` | `curl http://<vm-ip>:9100/metrics`; `systemctl status node_exporter` |
| `inference` | `curl http://api.mlops.local/metrics`; confirm the Service is resolvable from VM09 |
| `ingest` | `curl http://10.20.2.31:9101/metrics`; check the OPC-UA client is connected |
| `timescale_exporter` | `curl http://10.20.2.40:9187/metrics`; check the exporter's DSN credentials |
| `kubernetes-*` | `kubernetes_sd_configs` needs a working ServiceAccount token and RBAC |

**MLflow has no native Prometheus metrics.** This is a known limitation, not a broken target:
VM06 is scraped via `node_exporter` only, and the ML-specific story comes from the inference
and TimescaleDB metrics. If MLflow-level metrics are needed, front it with an exporter
sidecar — a code change, which means a signed bundle.

---

## Alerts and what they mean

| Alert | Meaning | First thing to check |
|---|---|---|
| `InferenceHighErrorRate` | 5xx > 5% over 5m | pod logs — usually the model raising on unexpected input |
| `InferenceHighLatency` | p95 > 500ms over 5m | HPA saturation, or TimescaleDB slow on the audit insert |
| `IngestionStalled` | tag rate near zero | the ingestion section at the top of this page |
| `SensorFlatline` | channel stddev ≈ 0 for > 24h | sensor/DAQ health; exclude the channel |
| `UnmappedTags` | tag mapping drift | update `ml/ingest/tag_mapping.yml` |
| `NoModelLoaded` | `inference_model_loaded == 0` for > 2m | the model-load section at the top of this page |
| `RegistryBackupStale` | MLflow/NAS backup older than N days | the backups section of `deployment-guide.md` |

Model-level alerts (Watch/Plan/Urgent/Stop tiers) are delivered by the alerting engine to
the CMMS, not by Prometheus — see the alert tiering section of the main spec §7.

---

## Training fails: `No Staging model found; nothing to evaluate`

`evaluate.py` exits `1`. Run `train.py` first — evaluation reads the `Staging` stage, it does
not train.

## CI/CD `Train` stage fails with exit code 2

Not an infrastructure failure — this is the quality gate working. The newly trained model's
precision regressed more than the tolerance in `ml/training/config.yml` against the current
`Production` model. Compare the two runs in MLflow before deciding whether the data changed,
the hyperparameters were a bad idea, or the tolerance needs revisiting.

## `terraform apply` succeeds but Ansible cannot reach the hosts

`ansible/inventory/hosts.ini` is generated, not committed. Regenerate it after any Terraform
change that alters IPs:

```bash
python3 scripts/generate-inventory.py > ansible/inventory/hosts.ini
```

Then check SSH reachability from VM01 specifically — `sg-mgmt` only opens port 22 to the
admin CIDR, so running Ansible from an unexpected source IP will time out on every host at
once.
