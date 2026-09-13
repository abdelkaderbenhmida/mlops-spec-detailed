# TODO: high - Add alert rule for ingestion stalls
# TODO: medium - Implement dashboard for drift detection
# TODO: low - Add prediction distribution monitoring
"""Data drift detection for the predictive maintenance pipeline.

Compares the current/inference data distribution against the reference
(training) data per numeric feature using a two-sample Kolmogorov-Smirnov
test. Produces an aggregate drift score (fraction of features that drifted)
written to ml/data/monitoring/drift_report.json so the retraining trigger can
consume it.

Numeric feature list and data paths come from ml/training/config.yml.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "training"))
from preprocess import load_config

CONFIG = load_config()
NUMERIC_FEATURES = CONFIG["features"]["numeric"]
DEFAULT_RAW_PATH = CONFIG["data"]["raw_path"]

# Kernel-smoothed reference; current is what inference/production sees.
DEFAULT_CURRENT_PATH = Path(CONFIG["data"].get("current_path", "ml/data/raw/maintenance.csv"))
REPORT_PATH = Path("ml/data/monitoring/drift_report.json")

KS_ALPHA = 0.05
KS_STAT_THRESHOLD = 0.1
DRIFT_HARD_THRESHOLD = float(
    os.environ.get("DRIFT_THRESHOLD", CONFIG.get("evaluation", {}).get("drift_threshold", 0.3))
)


def _load_numeric(df: pd.DataFrame) -> dict[str, np.ndarray]:
    pdf = df[NUMERIC_FEATURES].apply(pd.to_numeric, errors="coerce")
    return {col: pdf[col].dropna().to_numpy() for col in NUMERIC_FEATURES}


def detect_drift(
    reference_path: str | Path,
    current_path: str | Path = DEFAULT_CURRENT_PATH,
) -> dict:
    """Return per-feature KS results plus an aggregate drift score.

    score = fraction of numeric features flagged as drifted.
    """
    ref = pd.read_csv(reference_path)
    cur = pd.read_csv(current_path)

    ref_num = _load_numeric(ref)
    cur_num = _load_numeric(cur)

    features = {}
    flagged = []
    for col in NUMERIC_FEATURES:
        if col not in ref_num or col not in cur_num:
            features[col] = {"error": "column missing"}
            continue
        r, c = ref_num[col], cur_num[col]
        if r.size == 0 or c.size == 0:
            features[col] = {"error": "empty column"}
            continue
        stat, p = stats.ks_2samp(r, c)
        drifted = bool(p < KS_ALPHA and stat > KS_STAT_THRESHOLD)
        features[col] = {
            "ks_statistic": float(stat),
            "p_value": float(p),
            "drifted": drifted,
        }
        if drifted:
            flagged.append(col)

    drift_score = len(set(flagged)) / max(len(NUMERIC_FEATURES), 1)

    report = {
        "reference_path": str(reference_path),
        "current_path": str(current_path),
        "n_features": len(NUMERIC_FEATURES),
        "drift_score": drift_score,
        "threshold": DRIFT_HARD_THRESHOLD,
        "drift_detected": drift_score > DRIFT_HARD_THRESHOLD,
        "drifted_features": flagged,
        "features": features,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    logger.info("Drift score=%.3f threshold=%.3f detected=%s", drift_score, DRIFT_HARD_THRESHOLD, report["drift_detected"])
    return report


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = __import__("argparse").ArgumentParser(description="Drift detection")
    parser.add_argument("--reference", default=DEFAULT_RAW_PATH)
    parser.add_argument("--current", default=str(DEFAULT_CURRENT_PATH))
    args = parser.parse_args()
    report = detect_drift(args.reference, args.current)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
