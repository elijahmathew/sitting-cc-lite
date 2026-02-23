"""
recommendation.py — Map readiness score to a training recommendation and explanation.

Recommendation tiers:
    >= 80   → High intensity or long aerobic effort
    50–79   → Tempo or aerobic base work
    < 50    → Active recovery or full rest

Explanation:
    Selects the top 2 absolute contributors from the scoring dict and generates
    a short, plain-English sentence explaining today's score.
"""

from typing import Dict, Tuple


# Recommendation tiers with label and suggested workouts
TIERS = [
    {
        "min": 80,
        "label": "High Intensity / Long Aerobic",
        "detail": "Your body is primed. Today is the day for intervals, a race-pace effort, or your long session.",
        "color": "#2ecc71",
        "emoji": "🟢"
    },
    {
        "min": 50,
        "label": "Tempo / Aerobic Base",
        "detail": "Solid readiness. Stick to controlled, aerobic efforts — tempo runs, zone 2 rides, steady swims.",
        "color": "#f39c12",
        "emoji": "🟡"
    },
    {
        "min": 0,
        "label": "Recovery / Rest",
        "detail": "Your body is signaling stress. Prioritize an easy spin, yoga, or full rest today.",
        "color": "#e74c3c",
        "emoji": "🔴"
    },
]

# Human-readable descriptions for each feature contribution
FEATURE_LABELS = {
    "HRV vs Baseline": {
        "positive": "HRV is elevated above your baseline, indicating strong autonomic recovery",
        "negative": "HRV is suppressed below your baseline, a sign of accumulated stress",
    },
    "Resting HR vs Baseline": {
        "positive": "resting heart rate is lower than usual, suggesting good cardiovascular recovery",
        "negative": "resting heart rate is elevated above your baseline, a common fatigue indicator",
    },
    "Sleep Quality": {
        "positive": "sleep quality was above average last night",
        "negative": "sleep quality was below average, limiting overnight recovery",
    },
    "Training Load": {
        "positive": "training load is lighter than your chronic average, giving your body room to recover",
        "negative": "recent training load is higher than your chronic average, accumulating fatigue",
    },
}


def get_recommendation(score: float) -> Dict:
    """Return the recommendation tier dict for a given readiness score."""
    for tier in TIERS:
        if score >= tier["min"]:
            return tier
    return TIERS[-1]  # fallback to recovery


def get_explanation(contributions: Dict[str, float]) -> str:
    """
    Generate a plain-English explanation based on the top 2 absolute contributors.

    Args:
        contributions: dict of {feature_name: contribution_value}

    Returns:
        A short explanation string suitable for display.
    """
    if not contributions:
        return "Insufficient data to generate explanation."

    # Sort by absolute contribution, descending
    sorted_contribs = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
    top_two = sorted_contribs[:2]

    parts = []
    for feature, value in top_two:
        if feature not in FEATURE_LABELS:
            continue
        direction = "positive" if value >= 0 else "negative"
        parts.append(FEATURE_LABELS[feature][direction])

    if not parts:
        return "Score driven by combined metrics across HRV, sleep, and training load."

    if len(parts) == 1:
        return f"Today's score is primarily influenced by {parts[0]}."

    return f"Today's score is primarily driven by {parts[0]}, and {parts[1]}."


def get_full_recommendation(score: float, contributions: Dict[str, float]) -> Tuple[Dict, str]:
    """
    Convenience wrapper: returns both recommendation tier and explanation string.
    """
    rec = get_recommendation(score)
    explanation = get_explanation(contributions)
    return rec, explanation
