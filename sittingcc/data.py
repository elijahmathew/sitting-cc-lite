"""
data.py — Load and validate wearable/training CSV data.

Expected columns:
    date, hrv_ms, rhr_bpm, sleep_hours, sleep_score, strain
"""

import pandas as pd

REQUIRED_COLUMNS = {"date", "hrv_ms", "rhr_bpm", "sleep_hours", "sleep_score", "strain"}


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load CSV from filepath, parse dates, sort chronologically,
    and validate required columns are present.

    Returns a clean DataFrame indexed by integer, sorted by date.
    Raises ValueError if required columns are missing.
    """
    df = pd.read_csv(filepath, parse_dates=["date"])

    # Validate schema
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    # Sort chronologically — rolling calculations depend on order
    df = df.sort_values("date").reset_index(drop=True)

    # Basic type enforcement
    numeric_cols = ["hrv_ms", "rhr_bpm", "sleep_hours", "sleep_score", "strain"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with any null values in required fields
    df = df.dropna(subset=numeric_cols).reset_index(drop=True)

    return df
