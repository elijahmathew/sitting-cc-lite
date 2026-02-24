# 🚴 Sitting CC Lite

> *AI-powered daily training readiness — built on your wearable data.*

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square)
![Status](https://img.shields.io/badge/Status-v1.0-green?style=flat-square)

---

## Why This Exists

Modern wearables generate increasingly granular recovery data, but they rarely translate those signals into a clear daily decision. Sitting CC explores whether an interpretable AI layer can collapse recovery and training load into one explainable instruction: how hard should you train today?

---

## The Problem

Endurance athletes collect enormous amounts of biometric data — HRV, resting heart rate, sleep quality, training load — but most platforms don't answer the question that actually matters each morning:

**How hard should I train today?**

Generic training plans ignore how your body responded to yesterday's effort. Coaching is expensive and inaccessible. The result: athletes either overtrain and plateau, or undertrain out of guesswork.

**Sitting CC Lite** converts raw wearable data into a single, interpretable daily readiness score and a concrete training recommendation — with full transparency into what drove the number.

---

## Demo

Launch locally in 2 commands:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open `http://localhost:8501`. No account, no API key, no setup.

Upload your own CSV or use the included sample data (30 days of synthetic training data with realistic fatigue patterns).

---

## What It Does

| Feature | Description |
|---|---|
| **Readiness Score (0–100)** | Daily score based on HRV, resting HR, sleep quality, and training load vs. your personal baselines |
| **Training Recommendation** | Tiered recommendation (High Intensity / Tempo / Recovery) mapped to your score |
| **Contributing Factors** | Breaks down exactly which metrics drove today's number and by how much |
| **30-Day Trend Chart** | Readiness vs. strain over time to surface training load patterns |
| **Data Table** | Full history with progress-bar readiness scores |

---

## How It Works

```
CSV Input → Validate → Feature Engineering → Readiness Score → Recommendation + Explanation → UI
```

**Feature Engineering** (`sittingcc/features.py`): Computes rolling personal baselines — 7-day HRV, 7-day RHR, 28-day strain average — and derives deviation metrics. Raw values are meaningless without personal context; deviations from your own norm are predictive.

**Scoring** (`sittingcc/scoring.py`): Weighted formula starting from a base of 70:

```
score = 70
      + 120 × hrv_pct_deviation       # HRV above/below your 7-day baseline
      - 4   × rhr_delta_bpm           # RHR elevation above your 7-day baseline
      + 0.25 × (sleep_score - 75)     # Sleep quality above/below average
      - 15  × (strain_ratio - 1.0)    # Recent load vs. chronic 28-day average
```

**Recommendation** (`sittingcc/recommendation.py`): Maps score to tier and uses the top 2 absolute contributors to generate a plain-English explanation — so athletes understand *why*, not just *what*.

---

## Key Product Decisions

Full decision log in [`DECISIONS.md`](./DECISIONS.md). The three most important:

**1. Interpretable formula over a black-box model.**
Trust is the core product requirement. An athlete who doesn't understand a rest recommendation will ignore it. The formula exposes exactly which factors drove today's score. The tradeoff is accuracy — fixed weights aren't optimal for every athlete. A v2 would learn weights from labeled outcome data while preserving interpretability via SHAP values.

**2. Personal baselines over population norms.**
An HRV of 55ms is excellent for one athlete and concerning for another. All features are computed relative to the individual's rolling history. This makes recommendations meaningfully personalized at the cost of a cold-start period (~7 days of data).

**3. Daily decision over a weekly plan.**
Readiness is sensitive to the last 24–48 hours. A weekly plan generated Monday doesn't know about Wednesday's poor sleep. Scoping to a single-day recommendation makes the output more honest and more actionable — even if it creates a daily check-in habit requirement.

---

## CSV Schema

```
date, hrv_ms, rhr_bpm, sleep_hours, sleep_score, strain
```

Compatible with exports from WHOOP, Garmin, and Oura (with minor column renaming).

---

## Project Structure

```
sitting-cc-lite/
│
├── app.py                  # Streamlit UI entry point
├── requirements.txt
├── README.md
├── DECISIONS.md            # Product & engineering decision log
├── data/
│   └── sample.csv          # 30 days of synthetic training data
└── sittingcc/
    ├── data.py             # Load and validate CSV
    ├── features.py         # Rolling feature engineering
    ├── scoring.py          # Readiness score computation
    └── recommendation.py   # Recommendation mapping and explanation
```

---

## Roadmap

- **Feedback loop** — Thumbs up/down on daily recommendations to continuously refine weights
- **ML model** — Replace hand-tuned weights with gradient boosting trained on labeled outcome data
- **API integrations** — Direct pull from WHOOP, Garmin Connect, and Strava (no manual CSV export)
- **Training phase awareness** — Adjust thresholds based on build / peak / taper phase
- **Multi-sport support** — Differentiate strain by sport type; running and cycling have different recovery signatures

---

*Built by Elijah Mathew · [linkedin.com/in/elijahmathew](https://linkedin.com/in/elijahmathew)*
