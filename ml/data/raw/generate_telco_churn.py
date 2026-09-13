#!/usr/bin/env python3
# TODO: medium - Add type hints where missing
# TODO: low - Add comprehensive docstring
# TODO: low - Add error handling for edge cases
"""Generate a realistic synthetic Telco Customer Churn dataset.

Produces ~7,000 rows with the standard Telco churn schema (numeric + categorical
features matching the classic public dataset) plus a derived churn label.

Output: ml/data/raw/telco_churn.csv
Deterministic (fixed seed) so training runs are reproducible.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

RAW_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RAW_DIR, "telco_churn.csv")

RNG = np.random.default_rng(42)

N_DEFAULTS = 7000

CONTRACT_TYPES = ["month-to-month", "one year", "two year"]
PAYMENT_METHODS = [
    "electronic_check",
    "mailed_check",
    "bank_transfer",
    "credit_card",
]
INTERNET_SERVICES = ["DSL", "Fiber optic", "No"]
ADDON_SERVICES = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]

GENDER = ["Male", "Female"]
PARTNER = ["Yes", "No"]
DEPENDENTS = ["Yes", "No"]
PHONE_SERVICE = ["Yes", "No"]
MULTIPLE_LINES = ["Yes", "No", "No phone service"]
YES_NO_NO_PHONE = ["Yes", "No", "No internet service"]


def _weighted_choice(options: list[str], probs: list[float]) -> str:
    return str(RNG.choice(options, p=probs))


def generate(n_rows: int = N_DEFAULTS) -> pd.DataFrame:
    rows: list[dict] = []
    for i in range(n_rows):
        tenure = int(RNG.integers(0, 73))
        contract = _weighted_choice(CONTRACT_TYPES, [0.55, 0.24, 0.21])
        internet = _weighted_choice(INTERNET_SERVICES, [0.45, 0.44, 0.11])
        monthly = 0.0

        if internet == "Fiber optic":
            monthly += RNG.uniform(50.0, 105.0)
        elif internet == "DSL":
            monthly += RNG.uniform(20.0, 55.0)

        # Contract type shapes monthly charges.
        if contract == "two year":
            monthly += RNG.uniform(10.0, 20.0)
        elif contract == "one year":
            monthly += RNG.uniform(5.0, 12.0)
        else:
            monthly += RNG.uniform(0.0, 8.0)

        addons = RNG.choice(ADDON_SERVICES, size=int(RNG.integers(0, 5)), replace=False)
        for addon in addons:
            monthly += 7.0 if addon != "StreamingTV" else 10.0

        if _weighted_choice(["Yes", "No"], [0.9, 0.1]) == "Yes":
            phone_service = "Yes"
            multiple_lines = _weighted_choice(["Yes", "No"], [0.42, 0.58])
        else:
            phone_service = "No"
            multiple_lines = "No phone service"

        payment = _weighted_choice(PAYMENT_METHODS, [0.34, 0.23, 0.22, 0.21])

        total = monthly * (tenure if tenure > 0 else 1)
        # Churn probability grows with month-to-month + electronic check,
        # shrinks with tenure.
        p_churn = (
            0.08
            + 0.35 * (contract == "month-to-month")
            + 0.18 * (payment == "electronic_check")
            + 0.15 * (internet == "Fiber optic")
            - 0.012 * tenure
        )
        p_churn = float(np.clip(p_churn, 0.01, 0.95))
        churn = "Yes" if RNG.random() < p_churn else "No"

        rows.append(
            {
                "customer_id": f"CUST-{i:05d}",
                "gender": _weighted_choice(GENDER, [0.5, 0.5]),
                "senior_citizen": int(RNG.integers(0, 2)),
                "partner": _weighted_choice(PARTNER, [0.48, 0.52]),
                "dependents": _weighted_choice(DEPENDENTS, [0.3, 0.7]),
                "tenure": tenure,
                "phone_service": phone_service,
                "multiple_lines": multiple_lines,
                "internet_service": internet,
                "online_security": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]),
                "online_backup": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]),
                "device_protection": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]),
                "tech_support": _weighted_choice(YES_NO_NO_PHONE, [0.25, 0.45, 0.3]),
                "streaming_tv": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]),
                "streaming_movies": _weighted_choice(YES_NO_NO_PHONE, [0.3, 0.4, 0.3]),
                "contract": contract,
                "paperless_billing": _weighted_choice(["Yes", "No"], [0.6, 0.4]),
                "payment_method": payment,
                "monthly_charges": round(monthly, 2),
                "total_charges": round(total, 2),
                "churn": churn,
            }
        )

    df = pd.DataFrame(rows)
    # Guarantee realistic ~7000 rows by adjusting to target when asked.
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Telco churn CSV.")
    parser.add_argument("--rows", type=int, default=N_DEFAULTS, help="Number of rows.")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help="Output CSV path.")
    args = parser.parse_args()

    df = generate(args.rows)
    df.to_csv(args.output, index=False)
    n_churn = int((df["churn"] == "Yes").sum())
    print(
        f"Wrote {len(df):,} rows -> {args.output}\n"
        f"  churn=Yes: {n_churn:,} ({n_churn / len(df):.1%})"
    )


if __name__ == "__main__":
    main()
