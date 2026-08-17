# Training Guide

How to retrain locally, how to add a feature end to end, and what the promotion criteria
actually are.

## Layout

```
ml/
├── data/
│   ├── raw/telco_churn.csv          committed sample (~7k rows)
│   ├── raw/generate_telco_churn.py  regenerates the sample
│   └── processed/                   written by preprocess.py, not committed
├── notebooks/01-eda.ipynb           exploration, outside the pipeline
├── training/
│   ├── config.yml                   single source of truth for the pipeline
│   ├── preprocess.py                validation, imputation, stratified split
│   ├── features.py                  build_preprocessor() → ColumnTransformer
│   └── train.py                     fit, log, register, → Staging
└── evaluation/evaluate.py           Staging vs Production gate
```

## Retraining locally

```bash
export MLFLOW_TRACKING_URI=http://10.0.2.30:5000   # or http://localhost:5000
make train        # python3 ml/training/train.py
make evaluate     # python3 ml/evaluation/evaluate.py
```

`make train` registers a new `churn-model` version and moves it to `Staging`. It does not
touch `Production`.

To run everything offline against a local MLflow, point the tracking URI at a local server
(`mlflow server --backend-store-uri sqlite:///mlflow.db`) — the code paths are identical.

For a reproducible run matching CI, use the training image:

```bash
docker build -t mlops-training:latest -f docker/training/Dockerfile .
docker run --rm -e MLFLOW_TRACKING_URI=http://10.0.2.30:5000 mlops-training:latest
```

## Configuration

Everything tunable lives in `ml/training/config.yml` and is logged to MLflow as run
parameters, so any run can be traced back to the exact configuration that produced it.

```yaml
mlflow:
  tracking_uri: "http://10.0.2.30:5000"
  experiment_name: "churn_prediction"
  model_name: "churn-model"
  artifact_path: "model"

data:
  raw_path: "ml/data/raw/telco_churn.csv"
  test_size: 0.2
  random_state: 42
  target: "churn"

model:
  n_estimators: 200
  max_depth: 12
  min_samples_split: 10
  min_samples_leaf: 4
  max_features: "sqrt"
  class_weight: "balanced"

evaluation:
  probability_threshold: 0.5
  max_f1_regression: 0.01
```

Change hyperparameters here, not in the Python — the values are read at run time and logged
verbatim.

## Adding a new feature

A feature has to be added in four places or the serving layer will break at inference time.

1. **Data** — make sure the column exists in `ml/data/raw/telco_churn.csv` (and in
   `generate_telco_churn.py` if you use the generator).

2. **Config** — add the column name under `features.numeric` or `features.categorical` in
   `ml/training/config.yml`. `features.py` builds the `ColumnTransformer` from these lists,
   so nothing else in the training code needs to change.

3. **Validation** — if the column must never be null or has a bounded range, add the check
   in `ml/training/preprocess.py` alongside the existing schema checks. Failing early during
   training is much cheaper than a silent distribution shift.

4. **API schema** — add the field to `PredictRequest` in `api/app/schemas.py` with a
   sensible default and the same constraint set. **This step is mandatory**: the request is
   serialised with `model_dump(by_alias=True)` into a one-row DataFrame, so a field missing
   from the schema is a column missing from the model input. Give it a default so existing
   clients that do not send the field keep working.

5. **Tests** — extend `api/tests/test_predict.py` so the new field is exercised (valid
   value, invalid value → 422, default applied when omitted).

Then retrain: a new model version is registered, and only after promotion do the pods pick
it up. Because the API image is code-only, step 4 requires an image rebuild while steps 1–3
do not.

### Categorical values the model has not seen

`features.py` uses `OneHotEncoder(handle_unknown="ignore")`, so an unseen category encodes
as all zeros instead of raising. That keeps the API from 500-ing on unexpected input, but it
also means the model silently loses information — watch the prediction-distribution panel in
the Model Performance dashboard after any change to the set of allowed categories.

## Promotion criteria

| Transition | Trigger | Criterion |
|---|---|---|
| new version → `Staging` | automatic, at the end of `train.py` | none — every trained model is registered |
| `Staging` → `Production` | manual approval (Jenkins `input` step, or `train-and-register.sh --promote`) | `evaluate.py` must pass |

`evaluate.py` scores the `Staging` model and the current `Production` model on the same
held-out test set and computes:

```
threshold = production_f1 - max_f1_regression      # max_f1_regression = 0.01
promotable = staging_f1 >= threshold
```

Exit codes:

| Code | Meaning |
|---|---|
| `0` | Promotable — F1 holds within the 1% tolerance (or there is no Production model yet) |
| `1` | No `Staging` model found — nothing to evaluate |
| `2` | F1 regressed beyond tolerance — the CI/CD `Train` stage fails here and no approval is offered |

F1 is the gate metric rather than accuracy because churn is imbalanced; ROC-AUC is logged
alongside it for context but does not gate. Both metrics, for both models, are logged to an
MLflow run named `evaluate-staging`, so every promotion decision is auditable after the fact.

## Where the artifacts live

- **Runs, parameters, metrics** — MLflow on VM06, backed by the `mlflow` PostgreSQL database
  on VM08 (survives a VM06 rebuild).
- **Model artifacts** — MLflow artifact store on VM06's disk.
- **Registered versions and stages** — MLflow Model Registry (the source of truth for what
  is serving; `ml/models/` is local scratch only).
- **Prediction history** — `predictions` table in the `mlops` database on VM08.
