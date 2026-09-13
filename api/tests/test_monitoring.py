# TODO: high - Add alert rule for ingestion stalls
# TODO: medium - Implement dashboard for drift detection
# TODO: low - Add prediction distribution monitoring
"""Tests for the drift detector + retraining trigger (ml/monitoring/)."""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# allow importing ml.monitoring and ml/training helpers
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))
sys.path.insert(0, str(REPO_ROOT / "ml" / "training"))

from monitoring import drift_detector, retraining_trigger

NUMERIC = ["age_months", "operating_hours", "maintenance_history",
           "sensor_temp", "sensor_vibration", "sensor_pressure", "sensor_humidity"]


def _make_maintenance(tmp_path, n=300, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "machine_id": range(n),
        "equipment_type": rng.choice(["pump", "motor", "compressor", "turbine"], n),
        "age_months": rng.integers(1, 300, n),
        "operating_hours": rng.uniform(0, 200000, n),
        "maintenance_history": rng.integers(0, 100, n),
        "sensor_temp": rng.uniform(0, 200, n),
        "sensor_vibration": rng.uniform(0, 15, n),
        "sensor_pressure": rng.uniform(0, 100, n),
        "sensor_humidity": rng.uniform(0, 100, n),
        "failure_next_30_days": rng.binomial(1, 0.3, n),
    })
    path = tmp_path / "maintenance.csv"
    df.to_csv(path, index=False)
    return path


def test_no_drift_when_identical(tmp_path):
    ref = _make_maintenance(tmp_path, seed=1)
    det = drift_detector.detect_drift(ref, ref)
    assert det["drift_score"] == 0.0
    assert det["drift_detected"] is False


def test_drift_detected_on_shift(tmp_path):
    ref = _make_maintenance(tmp_path, seed=2)
    cur = pd.read_csv(_make_maintenance(tmp_path, seed=3))
    rng = np.random.default_rng(9)
    cur["sensor_vibration"] = cur["sensor_vibration"] * rng.normal(2.0, 0.4, size=len(cur))
    cur_path = tmp_path / "maintenance_shifted.csv"
    cur.to_csv(cur_path, index=False)
    det = drift_detector.detect_drift(ref, cur_path)
    assert det["drift_score"] > 0.0
    assert "sensor_vibration" in det["drifted_features"]


def test_trigger_fires_when_drifted(tmp_path):
    ref = _make_maintenance(tmp_path, seed=4)
    cur = pd.read_csv(ref)
    rng = np.random.default_rng(5)
    for col, mult, sd in [("sensor_vibration", 2.5, 0.5),
                          ("sensor_temp", 1.6, 0.4),
                          ("operating_hours", 1.8, 0.5)]:
        cur[col] = cur[col] * rng.normal(mult, sd, size=len(cur))
    cur_path = tmp_path / "maintenance_shifted2.csv"
    cur.to_csv(cur_path, index=False)
    det = drift_detector.detect_drift(ref, cur_path)
    assert det["drift_detected"] is True

    report_path = drift_detector.REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(det))
    result = retraining_trigger.trigger_retraining(dry_run=True)
    assert result["triggered"] is True
    assert result["dry_run"] is True


def test_trigger_does_not_fire_without_drift(tmp_path):
    ref = _make_maintenance(tmp_path, seed=6)
    det = drift_detector.detect_drift(ref, ref)
    report_path = drift_detector.REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(det))
    result = retraining_trigger.trigger_retraining(dry_run=True)
    assert result["triggered"] is False
