# Anvil — Plateforme MLOps Air-Gapped (README détaillé)

> Documentation complète du code source de **Anvil** (répertoire
> `mlops-platform-spec-detailed`) : description, outils, fonctionnement interne et procédure
> de test. Complète la [README principale](./README.md) et la
> [spécification](./mlops-platform-spec-detailed.md).
>
> **Emphase** : cette instance du code se concentre sur la **boucle ML locale** (maintenance
> prédictive, entraînement, registry, API FastAPI, monitoring) et la **provision
> d'infrastructure** (Terraform + Ansible). Des jeux de démonstration **maintenance** (AI4I
> 2020 synthétique) **et** **churn-télécom** coexistent pour exercer les composants
> plateforme ; le chemin ML principal est la **prédiction de défaillance équipement**.

---

## 1. Vue d'ensemble

**Anvil** est une plateforme MLOps **on-premise / air-gapped** pour la maintenance prédictive
dans des usines où les données de production ne peuvent pas quitter le site. Elle s'installe
dans la **DMZ de niveau 3.5** du site sur son propre hardware — 12 VMs, aucune connexion
internet.

Dans ce dépôt : de l'infrastructure-as-code (Terraform), de la configuration (Ansible),
un pipeline ML local (données maintenance + churn), une API FastAPI dans Kubernetes, un
monitoring Prometheus/Grafana, et une CI/CD offline (Jenkins + Gitea). Un déploiement Azure
AKS est aussi présent dans `azure/` (validation alternative).

---

## 2. Stack technique et rôle de chaque outil

| Domaine | Outil | Rôle dans Anvil |
|---|---|---|
| Infrastructure-as-Code | **Terraform** (libvirt / KVM) | 12 VMs DMZ `10.20.2.0/24` ; modules `compute`, `network`, `security-groups` |
| Config management | **Ansible** (~9 rôles) | Mirror d'abord, K8s, MLflow, TimescaleDB/Postgres, OPC-UA, monitoring, CI/CD |
| Orchestration | **Kubernetes** (namespace `mlops`) | Deployment `fastapi` + `hpa.yml`, ingress `api.mlops.local` |
| Tracking/Registry | **MLflow** (VM06 :5000) | Runs + registry modèle (`maintenance-model`) |
| DB | **TimescaleDB** (VM08) / Postgres | Télémetrie, prédictions, feedback, mlflow db |
| Ingestion OT | **OPC-UA** (VM07) | Client read-only egress, buffer store-and-forward, mapping de tags |
| Serving | **FastAPI** | `/predict`, `/health`, `/predict`, `/ingest/status` ; modèle tiré au pod startup |
| Monitoring | **Prometheus + Grafana** | node_exporter (12 VMs), API, cluster, model-performance |
| CI/CD | **Jenkins + Gitea** (offline) | test → train → evaluate → promotion manuelle → build → deploy |
| Réentraînement | Script local | Train + register → promote manuel Staging→Production |
| Tests | **pytest** + `make validate` | Tests API + validation statique (py_compile/yaml/json/tf/ansible) |

---

## 3. Structure du dépôt (détaillée)

```
anvil/  (mlops-platform-spec-detailed/)
├── Makefile                    # init/plan/apply/inventory/configure/bootstrap/train/evaluate/promote/build-image/deploy-k8s/smoke/validate/azure-validate
├── terraform/                  # libvirt/KVM (module compute, network, security-groups)
│   ├── main.tf, backend.tf, variables.tf, outputs.tf, terraform.tfvars.example
├── azure/                      # variante AKS (validation) — main.tf, modules/mlops-cluster, deploy/*.yaml
├── ansible/
│   ├── site.yml
│   ├── inventory/ (hosts.ini, group_vars/{all,k8s,mlflow}.yml)
│   ├── playbooks/ (01-common … 07-monitoring)
│   └── roles/ (common, docker, k8s-common, k8s-control-plane, k8s-worker,
│              mlflow, postgresql, node_exporter, prometheus, grafana, cicd)
├── ml/
│   ├── data/raw/ (generate_maintenance_data.py, generate_telco_churn.py, maintenance.csv, telco_churn.csv)
│   ├── data/processed/ (maintenance_processed.csv, encoders.joblib)
│   ├── training/ (train.py, features.py, preprocess.py, config.yml)
│   ├── evaluation/evaluate.py
│   └── notebooks/01-eda.ipynb
├── api/
│   ├── main.py                  # entrée FastAPI
│   └── app/
│       ├── db.py, metrics.py, model_loader.py, schemas.py
│       └── routers/ (health.py, predict.py)
│   ├── tests/ (conftest.py, test_health.py, test_predict.py)
│   └── requirements.txt
├── kubernetes/                 # namespace.yml, fastapi/{deployment,service,ingress,configmap,secret}.yml, hpa.yml
├── monitoring/
│   ├── prometheus/ (prometheus.yml, alert.rules.yml)
│   └── grafana/dashboards/ (fastapi-requests, kubernetes-cluster, model-performance, node-exporter .json)
├── cicd/Jenkinsfile + stages/{test,train,build,deploy}.sh
├── docker/ (fastapi/Dockerfile, mlflow/Dockerfile, training/Dockerfile)
├── scripts/ (bootstrap.sh, generate-inventory.py, smoke-test.sh, train-and-register.sh)
├── ui/index.html
└── docs/ (architecture, api-documentation, deployment-guide, ml-pipeline-diagram,
           infrastructure-diagram, training-guide, troubleshooting)
```

---

## 4. Fonctionnement pas à pas

### 4.1 Données

- `ml/data/raw/generate_maintenance_data.py` → `maintenance.csv` (40 000 lignes, failure_rate
  0.20, seed 42, 4 types d'équipement pump/motor/compressor/turbine) — le dataset **principal**
  pour la maintenance prédictive (schéma aligné sur le contrat API et la pipeline ML).
- `ml/data/raw/generate_telco_churn.py` → `telco_churn.csv` (churn, second jeu de démo).
- `ml/data/processed/maintenance_processed.csv` + `encoders.joblib` (artefacts de traitement).

### 4.2 Pipeline ML local (config dans `ml/training/config.yml`)

Cible : **`failure_next_30_days`** (binaire). Features numériques (age_months,
operating_hours, maintenance_history, sensor_temp/vibration/pressure/humidity) + catégorielle
(equipment_type).

- `ml/training/features.py`, `ml/training/preprocess.py` : validation, imputation, encodage,
  scaling, split (`load_and_preprocess`).
- `ml/training/train.py` : `RandomForestClassifier` (`class_weight="balanced"`, n_estimators
  200, max_depth 12), logue F1/AUC/recall dans MLflow, enregistre **`maintenance-model`** au
  registry + transition **Staging**.
- `ml/evaluation/evaluate.py` : compare la nouvelle version Staging vs Production (tolérance
  de précision).
- `scripts/train-and-register.sh --promote` : **gate manuelle** Staging → Production.

```bash
make train         # MLFLOW_TRACKING_URI=http://10.0.2.30:5000 python ml/training/train.py
make evaluate      # évaluation Staging vs Production
make promote       # scripts/train-and-register.sh --promote
```

### 4.3 API FastAPI (`api/`, `api/main.py`)

Structure par `app/` + `routers/` :
- `app/db.py` — SQLAlchemy (session + `PredictionLog`, table des prédictions).
- `app/metrics.py` — métriques Prometheus.
- `app/model_loader.py` — chargement du modèle depuis MLflow **au pod startup** (jamais
  embarqué dans l'image) + gestion de version (`model_metadata()`).
- `app/schemas.py` — `PredictRequest` / `PredictResponse` (fenêtre de capteurs).
- `app/routers/health.py` — `GET /health`.
- `app/routers/predict.py` — `POST /predict` : charge le modèle (503 si non chargé), calcule
  `predict_proba`, mappe en niveau de risque `_risk_level` (critical ≥0.7, high ≥0.4,
  medium ≥0.2, sinon low), écrit la prédiction en DB (`PredictionLog`), renvoie la réponse.

### 4.4 Infrastructure (Terraform)

`terraform/` : module `network` (DMZ, subnets), `compute` (instances 10.20.2.x), 
`security-groups`. 12 VMs prévues (bootstrap/ctrl-node, gitea-jenkins, k8s cp/2 workers,
mlflow, ingest OPC-UA, timescale, prometheus, grafana, training, registry-mirror).
La variante `azure/` (module `mlops-cluster`, deploy/*.yaml) valide le même design sur AKS.

### 4.5 Configuration (Ansible, mirror-first)

9 playbooks orchestrant les rôles : `common`, `docker`, `k8s-*` (contrôle + workers),
`mlflow`, `postgresql`, `node_exporter`, `prometheus`, `grafana`, `cicd`. Le **mirror
offline** (artefacts Helm/devpi/aptly/charts) est provisionné en premier, puis chaque
composant tire depuis ce miroir — aucun accès public.

### 4.6 Kubernetes

`kubernetes/` : namespace `mlops`, Deployment `fastapi` (+ configmap/secret/ingress), HPA.
Le Deployment tire le modèle du registry MLflow via `model_loader.py` au démarrage des pods.
`make deploy-k8s` applique namespace → fastapi → hpa et relance pour recharger le modèle.

### 4.7 Monitoring

`monitoring/prometheus/prometheus.yml` + `alert.rules.yml` ; 4 dashboards Grafana
(`fastapi-requests`, `kubernetes-cluster`, `model-performance`, `node-exporter`). `node_exporter`
sur toutes les VMs ; `timescale_exporter` sur VM08.

---

## 5. Procédure de test

### 5.1 Validation statique rapide (`make validate`)

```bash
make validate
# py_compile tous les .py → lint yaml → lint json → terraform validate → ansible syntax-check
```
(Terraform/Ansible peuvent se "SKIP" si les providers ne sont pas téléchargeables hors réseau.)

### 5.2 Tests API (pytest)

```bash
cd api && python -m pytest tests/ -v
#   test_health.py  → GET /health
#   test_predict.py → POST /predict (fenêtre valide, erreurs de schéma)
```
`tests/conftest.py` met en place le client de test FastAPI ; le chargement du modèle peut être
monkeypatched pour des tests sans MLflow.

### 5.3 Exécution pipeline

```bash
make train       # entraîne + enregistre + Staging (nécessite MLflow joignable)
make evaluate    # compare Staging vs Production
make smoke       # scripts/smoke-test.sh : POST une fenêtre d'exemple vers /predict
```

### 5.4 Déploiement K8s + smoke

```bash
make build-image
make deploy-k8s
make smoke
```

### 5.5 Validation Azure alternative

```bash
make azure-validate    # terraform validate sur azure/
```

---

## 6. Points d'attention (audit du code)

1. **Deux jeux de démonstration** : le code embarque de la donnée **maintenance** (chemin ML
   principal, modèle `maintenance-model`) **et** de la donnée **churn télécom**. Le Makefile
   et certains scripts citent encore "churn model" en some cibles — le modèle réellement
   servi par l'API est le `maintenance-model` (classeur RandomForest, prédiction de
   défaillance à 30 j).
2. **MLflow local** : le registry est standalone sur un VM (plus simple pour l'air-gap),
   contrairement à un control plane partagé ; artefacts sur disque local/NAS.
3. **Modèle non embarqué** : l'image n'incorpore pas le modèle — il est tiré du registry au
   démarrage (bonne pratique) ; un redéploiement/rollout est requis pour changer de version.
4. **Secrets Kubernetes** : `secret.yml` doit être remplacé par des vraies valeurs (Sealed
   Secrets hors air-gap, ou gestion locale) — ne pas commiter de mots de passe.
5. **Air-gap** : jamais de tag `latest`, miroir N-2, bundles signés sur média approuvé,
   sauvegardes NAS et drill de restauration trimestriels sont requis par la spec (voir
   `docs/deployment-guide.md`).

---

## 7. Références

- [README principale](./README.md) — vue d'ensemble et quickstart.
- [`mlops-platform-spec-detailed.md`](./mlops-platform-spec-detailed.md) — spec complète.
- [`ENTERPRISE-UPGRADE.md`](./ENTERPRISE-UPGRADE.md) — montée en version enterprise.
- `docs/architecture.md` — diagramme des décisions + diagramme des composants.
- `docs/api-documentation.md`, `docs/training-guide.md`, `docs/deployment-guide.md`,
  `docs/troubleshooting.md`.
- `Makefile` — cibles `validate`, `train`, `smoke`, `deploy-k8s`, `azure-validate`.
