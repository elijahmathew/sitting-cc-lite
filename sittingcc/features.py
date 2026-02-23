"""
features.py — Compute rolling features used by the readiness scoring model.

Features computed:
    hrv_baseline_7d     → 7-day rolling average HRV (personal baseline)
    rhr_baseline_7d     → 7-day rolling average RHR (personal baseline)
    strain_avg_28d      → 28-day rolling average strain (chronic load)
    hrv_pct             → today's HRV relative to 7d baseline (positive = above baseline)
    rhr_delta           → today's RHR minus 7d baseline (positive = elevated = bad)
    strain_ratio        → today's strain divided by 28d average (>1 = above normal load)

Design note:
    Ratios and deltas relative to personal baselines are more meaningful than raw values.
    An HRV of 55ms is great for one athlete and poor for another; deviation from your own
    norm is what actually predicts next-day readiness.
"""

import pandas as pd


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add rolling feature columns to the DataFrame.
    Requires at least 7 rows for meaningful HRV/RHR baselines.
    Rows with insufficient history will have NaN features (handled downstream).
    """
    df = df.copy()

    # 7-day rolling baselines (min_periods=3 to allow early rows to still score)
    df["hrv_baseline_7d"] = (
        df["hrv_ms"].rolling(window=7, min_periods=3).mean()
    )
    df["rhr_baseline_7d"] = (
        df["rhr_bpm"].rolling(window=7, min_periods=3).mean()
    )

    # 28-day rolling strain average (chronic training load)
    df["strain_avg_28d"] = (
        df["strain"].rolling(window=28, min_periods=7).mean()
    )

    # HRV percent deviation from baseline
    # Positive means HRV is above baseline (good), negative means suppressed (bad)
    df["hrv_pct"] = (df["hrv_ms"] - df["hrv_baseline_7d"]) / df["hrv_baseline_7d"]

    # RHR delta from baseline
    # Positive means heart rate is elevated above normal (bad sign)
    df["rhr_delta"] = df["rhr_bpm"] - df["rhr_baseline_7d"]

    # Strain ratio: today's strain vs chronic average
    # > 1.0 means training harder than usual; < 1.0 means backing off
    df["strain_ratio"] = df["strain"] / df["strain_avg_28d"].replace(0, 1)

    return df
