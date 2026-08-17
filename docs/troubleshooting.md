# Troubleshooting

Failure modes this platform actually produces, in rough order of how often they bite.

---

## Pod starts but `/health` says `model_loaded: false`

`api/app/model_loader.py` deliberately catches every exception during load so the process
stays up and reports its state instead of crash-looping. The real error is in the pod log:

```bash
kubectl logs -n mlops deployment/fastapi | grep -i "Failed to load model"
```

Common causes:

| Symptom in the log | Cause | Fix |
|---|---|---|
| `RESOURCE_DOES_NOT_EXIST: Registered Model with name=churn-model not found` | Nothing has been trained yet | `./scripts/train-and-register.sh --promote` |
| `No versions ... with stage Production` | A version exists but only in `Staging` | Promote it — `make promote` |
| `Connection refused` / `Max retries exceeded` on port 5000 | MLflow on VM06 is down, or `MLFLOW_TRACKING_URI` is wrong | `curl http://10.0.2.30:5000/health`; check `kubernetes/fastapi/configmap.yml` |
| `PermissionError` on the artifact path | Artifact store permissions (see below) | fix ownership on VM06 |
| `ModuleNotFoundError` for scikit-learn or a version mismatch | Training image and serving image disagree on library versions | pin the same versions in `docker/training/Dockerfile` and `api/requirements.txt` |

Note that the pod stays `Running` in all these cases. If the readiness probe is configured to
require `status == "healthy"`, the pod will correctly stay out of the Service and no traffic
is served by a model-less replica.

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
  directory that only exists on VM06. Either mount it, or move to object storage
  (`s3://…`/GCS) — which is the right answer as soon as more than one host trains.
- After changing ownership, restart the service: `sudo systemctl restart mlflow`.

---

## Model loads locally but not in the pod

Almost always DNS or network policy, not MLflow:

```bash
kubectl run -n mlops nettest --rm -it --image=curlimages/curl -- \
  curl -s http://10.0.2.30:5000/health
```

If that fails, the cluster nodes cannot reach VM06 — check `sg-internal` covers the pod CIDR,
not just the node subnet.

---

## Promotion took effect in MLflow but the API still serves the old version

Expected. The model is loaded once, in the FastAPI `lifespan` startup hook. Nothing polls the
registry.

```bash
kubectl rollout restart deployment/fastapi -n mlops
kubectl rollout status deployment/fastapi -n mlops
curl http://api.mlops.local/model-info   # confirm the new version
```

`cicd/stages/deploy.sh` does this automatically; it is only a surprise when someone promotes
by hand.

---

## PostgreSQL connection pool exhaustion

Symptom: `/predict` still returns `200` but the logs fill with

```
Failed to log prediction to DB: QueuePool limit of size 5 overflow 10 reached
```

Predictions are still correct — the audit write is best-effort — but the history has holes.

- The engine is configured in `api/app/db.py` with `pool_size=5, max_overflow=10`, so each
  replica can hold up to 15 connections. Multiply by the replica count *and* by the HPA
  maximum before comparing against PostgreSQL's `max_connections` (default 100).
- Fixes, in order of preference: lower the HPA maximum, raise `max_connections` on VM08, or
  put PgBouncer in front of VM08.
- Check current usage: `psql -h 10.0.2.40 -U mlops_app -d mlops -c "SELECT count(*) FROM pg_stat_activity;"`
- `pool_pre_ping=True` and `pool_recycle=3600` are already set, so stale connections after a
  Postgres restart are not the cause.

---

## `predictions` table growth

Every request inserts a row with a JSONB payload. On a busy endpoint this is the fastest
growing thing in the platform, and `postgres_exporter` on VM08 exposes table size for exactly
this reason.

```sql
SELECT pg_size_pretty(pg_total_relation_size('predictions'));
```

Add a retention job (drop or archive rows older than N days) before this becomes urgent.
There is no retention policy in the repo by design — the right window depends on how far back
drift analysis needs to look.

---

## Prometheus scrape target down

Check `http://10.0.2.50:9090/targets` first, then match the target:

| Target | Check |
|---|---|
| `node_exporter` | `curl http://<vm-ip>:9100/metrics`; `systemctl status node_exporter` |
| `fastapi` | `curl http://api.mlops.local/metrics`; confirm the Service is resolvable from VM09 |
| `postgres_exporter` | `curl http://10.0.2.40:9187/metrics`; check the exporter's DSN credentials |
| `kubernetes-*` | `kubernetes_sd_configs` needs a working ServiceAccount token and RBAC |

**MLflow has no native Prometheus metrics.** This is a known limitation, not a broken target:
VM06 is scraped via `node_exporter` only, and the ML-specific story comes from the FastAPI
and PostgreSQL metrics. If MLflow-level metrics are needed, front it with an exporter
sidecar.

---

## Alerts and what they mean

| Alert | Meaning | First thing to check |
|---|---|---|
| `FastAPIHighErrorRate` | 5xx > 5% over 5m | pod logs — usually the model raising on unexpected input |
| `FastAPIHighLatency` | p95 > 500ms over 5m | HPA saturation, or Postgres slow on the audit insert |
| `PredictionVolumeDrop` | request count near zero | upstream integration, Ingress, or a bad rollout |
| `NoModelLoaded` | `fastapi_model_loaded == 0` for > 2m | the model-load section at the top of this page |

---

## Training fails: `No Staging model found; nothing to evaluate`

`evaluate.py` exits `1`. Run `train.py` first — evaluation reads the `Staging` stage, it does
not train.

## CI/CD `Train` stage fails with exit code 2

Not an infrastructure failure — this is the quality gate working. The newly trained model's
F1 regressed more than `evaluation.max_f1_regression` (1%) against the current `Production`
model. Compare the two runs in MLflow before deciding whether the data changed, the
hyperparameters were a bad idea, or the tolerance needs revisiting.

## `terraform apply` succeeds but Ansible cannot reach the hosts

`ansible/inventory/hosts.ini` is generated, not committed. Regenerate it after any Terraform
change that alters IPs:

```bash
python3 scripts/generate-inventory.py > ansible/inventory/hosts.ini
```

Then check SSH reachability from VM01 specifically — `sg-mgmt` only opens port 22 to the
admin CIDR, so running Ansible from an unexpected source IP will time out on every host at
once.
