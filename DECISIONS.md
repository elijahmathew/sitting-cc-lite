# DECISIONS.md — Product & Engineering Decision Log

> This document records the key decisions made in building Sitting CC Lite, the reasoning behind each, and known limitations. Decisions made explicitly are better than decisions made by default.

---

## 1. Daily Decision Instead of Weekly Plan

**Decision:** The model outputs a single-day readiness score and recommendation, not a multi-day or weekly training plan.

**Why:**
Training readiness is highly sensitive to the previous 24–48 hours. A weekly plan generated Monday morning doesn't know that you had 5 hours of fragmented sleep Wednesday night, or that Thursday's ride left your HRV suppressed for two days. Generating a 7-day plan implies a confidence in future prediction that the data doesn't support.

Scoping to a daily decision has two benefits: the output is more honest (it reflects what we actually know), and it's more actionable (you check it each morning and it tells you exactly what to do today).

The tradeoff is that athletes need to check the app daily rather than set a plan once. That's a real friction cost. A v2 might offer a provisional weekly view with explicit low-confidence flags on days beyond 48 hours.

---

## 2. Interpretable Scoring Formula Instead of Deep Learning

**Decision:** Use a transparent weighted formula with hand-tuned parameters rather than a neural network or complex ensemble model.

**Why:**
An athlete who gets a score of 42 and a recommendation to rest will not change their behavior unless they understand why. A black-box model that outputs a number without explanation is not a useful product — it's a magic 8-ball. The current formula exposes exactly which factors drove today's number and by how much.

The deeper reason: trust is the core product requirement. If the model tells you to skip a workout you were excited for, you need to believe it. Interpretability is the mechanism for earning that trust over time.

The tradeoff is accuracy. Hand-tuned weights derived from domain knowledge and sports science literature are not necessarily the optimal weights for any given athlete. A v2 would learn these weights from labeled outcome data while preserving interpretability through tools like SHAP values.

---

## 3. Personal Data First, Not Population Data

**Decision:** All features are computed relative to the individual athlete's rolling baselines, not population-level norms.

**Why:**
Physiology varies enormously between athletes. An HRV of 55ms is excellent for a 45-year-old recreational cyclist and concerning for an elite 25-year-old runner. A resting heart rate of 48bpm is normal for one athlete and elevated for another. Using population norms would produce systematically biased recommendations for anyone outside the average.

Rolling personal baselines (7-day for HRV and RHR, 28-day for strain) capture what "normal" looks like for this specific athlete. Deviations from personal baseline are far more predictive of next-day performance than raw values.

The tradeoff is cold start: the model needs at least 7 days of data before it can produce meaningful scores, and improves further with more history. Athletes with only a few days of data will see limited output.

---

## 4. Known Limitations

**Labeling Problem (most significant)**
The scoring formula uses hand-tuned weights, not weights learned from labeled outcome data. We don't yet have a ground truth label for "how did the athlete actually perform today relative to their potential?" Subjective ratings are noisy. Objective benchmarks (pace or power at a fixed heart rate zone, measured consistently) would be more reliable but require structured testing protocols.

**Lag in Rolling Windows**
The 28-day strain average means the model is slow to respond to abrupt changes in training load — a sudden reduction in training volume takes weeks to fully register in the chronic average. Athletes who significantly change their training will see a temporary mismatch in recommendations.

**Single-day Strain Input**
The current schema treats strain as a single daily value. In reality, two athletes with identical strain scores might have very different recovery needs depending on the type of training (running vs. cycling, intensity vs. volume). A future version should accept sport-type tags alongside strain values.

**No Feedback Loop**
The model doesn't learn from user behavior. If an athlete consistently ignores rest recommendations and performs fine, the model has no way to know. A feedback mechanism (even a simple thumbs up/down on each recommendation) would enable continuous model improvement over time.

**Sample Data is Synthetic**
The included `data/sample.csv` was generated to exhibit realistic fatigue patterns (high strain suppresses HRV, elevates RHR, reduces sleep quality over multi-day blocks) but is not real athlete data. Real data is messier, with more noise, missing values, and irregular patterns.

---

*Last updated: January 2026*
