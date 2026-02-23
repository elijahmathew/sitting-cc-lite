"""
scoring.py — Compute interpretable readiness score (0–100) and feature contributions.

Scoring formula:
    Base score = 70 (neutral starting point)

    Contributions:
        HRV factor:     +120 * hrv_pct
            → HRV 10% above baseline adds ~12 points; 10% below subtracts ~12
        RHR factor:     -4 * rhr_delta
            → Each bpm above baseline costs 4 points; below baseline adds 4
        Sleep factor:   +0.25 * (sleep_score - 75)
            → Sleep score of 85 adds 2.5 points; score of 55 subtracts 5
        Strain factor:  -15 * (strain_ratio - 1.0)
            → Strain 50% above chronic average costs 7.5 points

    Final score is clamped to [0, 100].

Design note:
    Weights are hand-tuned based on sports science literature and domain knowledge.
    HRV is weighted most heavily because it's the most sensitive and validated
    marker of autonomic recovery. A v2 would learn weights from labeled outcome data.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict


BASE_SCORE = 70.0

# Contribution weights — see module docstring for rationale
WEIGHTS = {
    "hrv_pct":     120.0,
    "rhr_delta":   -4.0,
    "sleep_score": 0.25,   # applied as 0.25 * (sleep_score - 75)
    "strain_ratio": -15.0, # applied as -15 * (strain_ratio - 1.0)
}


def compute_score(row: pd.Series) -> Tuple[float, Dict[str, float]]:
    """
    Compute readiness score for a single row (a single day).

    Returns:
        score (float): final clamped readiness score 0–100
        contributions (dict): each feature's contribution to the score delta from base
    """
    contributions = {}

    # HRV deviation contribution
    hrv_contrib = WEIGHTS["hrv_pct"] * row.get("hrv_pct", 0)
    contributions["HRV vs Baseline"] = round(hrv_contrib, 1)

    # RHR deviation contribution
    rhr_contrib = WEIGHTS["rhr_delta"] * row.get("rhr_delta", 0)
    contributions["Resting HR vs Baseline"] = round(rhr_contrib, 1)

    # Sleep quality contribution (centered at 75)
    sleep_contrib = WEIGHTS["sleep_score"] * (row.get("sleep_score", 75) - 75)
    contributions["Sleep Quality"] = round(sleep_contrib, 1)

    # Strain ratio contribution (centered at 1.0)
    strain_ratio = row.get("strain_ratio", 1.0)
    strain_contrib = WEIGHTS["strain_ratio"] * (strain_ratio - 1.0)
    contributions["Training Load"] = round(strain_contrib, 1)

    # Sum contributions on top of base
    raw_score = BASE_SCORE + sum(contributions.values())

    # Clamp to valid range
    final_score = float(np.clip(raw_score, 0, 100))

    return final_score, contributions


def score_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply compute_score to every row in the DataFrame.
    Adds a 'readiness_score' column.
    Skips rows where required features are NaN.
    """
    df = df.copy()
    scores = []

    for _, row in df.iterrows():
        # Skip rows without enough rolling history
        if pd.isna(row.get("hrv_pct")) or pd.isna(row.get("rhr_delta")):
            scores.append(np.nan)
        else:
            score, _ = compute_score(row)
            scores.append(score)

    df["readiness_score"] = scores
    return df
