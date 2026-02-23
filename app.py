"""
app.py — Sitting CC Lite | Streamlit UI

Entry point. Run with:
    streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st
import altair as alt

from sittingcc.data import load_data
from sittingcc.features import compute_features
from sittingcc.scoring import compute_score, score_dataframe
from sittingcc.recommendation import get_full_recommendation

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sitting CC Lite",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main {
        background-color: #0d0d0d;
        color: #f0f0f0;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    h1, h2, h3 {
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        letter-spacing: -0.03em;
    }

    .score-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
    }

    .score-number {
        font-family: 'DM Mono', monospace;
        font-size: 5rem;
        font-weight: 500;
        line-height: 1;
        margin: 0;
    }

    .score-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #666;
        margin-top: 0.5rem;
    }

    .rec-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        height: 100%;
    }

    .rec-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #666;
        margin-bottom: 0.5rem;
    }

    .rec-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }

    .rec-detail {
        font-size: 0.9rem;
        color: #aaa;
        line-height: 1.5;
    }

    .explanation-card {
        background: #111;
        border-left: 3px solid #444;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.5rem;
        font-size: 0.9rem;
        color: #bbb;
        line-height: 1.6;
        margin-top: 1rem;
    }

    .contrib-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.4rem 0;
        border-bottom: 1px solid #1e1e1e;
        font-size: 0.875rem;
    }

    .contrib-pos { color: #2ecc71; font-family: 'DM Mono', monospace; }
    .contrib-neg { color: #e74c3c; font-family: 'DM Mono', monospace; }

    .stMetric {
        background: #1a1a1a;
        border-radius: 12px;
        padding: 1rem;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    .section-header {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: #555;
        margin-bottom: 1rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🚴 Sitting CC Lite")
st.markdown(
    "<p style='color:#666; font-size:0.95rem; margin-top:-0.5rem;'>"
    "AI-powered daily training readiness — built on your wearable data."
    "</p>",
    unsafe_allow_html=True
)
st.divider()


# ── File Upload ───────────────────────────────────────────────────────────────
SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "data", "sample.csv")

uploaded_file = st.file_uploader(
    "Upload your wearable data CSV",
    type=["csv"],
    help="Columns required: date, hrv_ms, rhr_bpm, sleep_hours, sleep_score, strain"
)

if uploaded_file:
    filepath = uploaded_file
    st.success("Using your uploaded data.")
else:
    filepath = SAMPLE_PATH
    st.info("No file uploaded — showing sample data (30 days of synthetic training data).")


# ── Load + Process ─────────────────────────────────────────────────────────────
try:
    df_raw = load_data(filepath)
    df_feat = compute_features(df_raw)
    df_scored = score_dataframe(df_feat)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Drop rows without enough rolling history to score
df_valid = df_scored.dropna(subset=["readiness_score"]).copy()

if df_valid.empty:
    st.error("Not enough data to compute scores. Need at least 3 days of data.")
    st.stop()

# Add recommendations column for the table
recs = []
for _, row in df_valid.iterrows():
    _, contributions = compute_score(row)
    rec, _ = get_full_recommendation(row["readiness_score"], contributions)
    recs.append(rec["label"])
df_valid["recommendation"] = recs


# ── Today's Analysis (most recent row) ────────────────────────────────────────
latest = df_valid.iloc[-1]
today_score, today_contribs = compute_score(latest)
today_rec, today_explanation = get_full_recommendation(today_score, today_contribs)

# Score color
if today_score >= 80:
    score_color = "#2ecc71"
elif today_score >= 50:
    score_color = "#f39c12"
else:
    score_color = "#e74c3c"

st.markdown("<div class='section-header'>Today's Readiness</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.markdown(f"""
    <div class="score-card">
        <div class="score-number" style="color:{score_color}">{today_score:.0f}</div>
        <div class="score-label">Readiness Score</div>
        <div style="margin-top:1rem; font-size:1.5rem">{today_rec['emoji']}</div>
        <div style="color:{score_color}; font-size:0.85rem; margin-top:0.25rem; font-weight:500">
            {today_rec['label']}
        </div>
        <div style="color:#555; font-size:0.75rem; margin-top:0.5rem;">
            {latest['date'].strftime('%A, %B %-d')}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="rec-card">
        <div class="rec-label">Recommendation</div>
        <div class="rec-title" style="color:{score_color}">{today_rec['label']}</div>
        <div class="rec-detail">{today_rec['detail']}</div>
        <div class="explanation-card">💡 {today_explanation}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Contributing Factors ───────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Contributing Factors</div>", unsafe_allow_html=True)

contrib_html = ""
for feature, value in sorted(today_contribs.items(), key=lambda x: abs(x[1]), reverse=True):
    sign = "+" if value >= 0 else ""
    cls = "contrib-pos" if value >= 0 else "contrib-neg"
    bar_width = min(abs(value) / 20 * 100, 100)
    bar_color = "#2ecc71" if value >= 0 else "#e74c3c"
    contrib_html += f"""
    <div class="contrib-row">
        <span style="color:#aaa; width:220px">{feature}</span>
        <div style="flex:1; margin:0 1rem; background:#1e1e1e; border-radius:4px; height:6px; overflow:hidden">
            <div style="width:{bar_width}%; background:{bar_color}; height:100%; border-radius:4px;"></div>
        </div>
        <span class="{cls}">{sign}{value}</span>
    </div>
    """

st.html(
    f'<div style="background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; padding:1.25rem 1.5rem; font-family:\'DM Sans\',sans-serif">'
    f'{contrib_html}</div>'
)


# ── Trend Chart ────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>30-Day Trend</div>", unsafe_allow_html=True)

chart_df = df_valid[["date", "readiness_score", "strain"]].copy()
chart_df["date"] = pd.to_datetime(chart_df["date"])

# Normalize strain to 0–100 scale for visual comparison
strain_max = chart_df["strain"].max()
chart_df["strain_normalized"] = (chart_df["strain"] / strain_max * 100).round(1)

# Melt for Altair
melted = chart_df.melt(
    id_vars="date",
    value_vars=["readiness_score", "strain_normalized"],
    var_name="metric",
    value_name="value"
)
melted["metric"] = melted["metric"].map({
    "readiness_score": "Readiness Score",
    "strain_normalized": "Strain (normalized)"
})

color_scale = alt.Scale(
    domain=["Readiness Score", "Strain (normalized)"],
    range=["#2ecc71", "#e74c3c"]
)

chart = alt.Chart(melted).mark_line(
    interpolate="monotone",
    strokeWidth=2.5
).encode(
    x=alt.X("date:T", title=None, axis=alt.Axis(labelColor="#666", gridColor="#1e1e1e")),
    y=alt.Y("value:Q", title=None, scale=alt.Scale(domain=[0, 105]),
            axis=alt.Axis(labelColor="#666", gridColor="#1e1e1e")),
    color=alt.Color("metric:N", scale=color_scale, legend=alt.Legend(
        orient="top-left",
        labelColor="#aaa",
        titleColor="#666",
        labelFontSize=12,
    )),
    tooltip=["date:T", "metric:N", "value:Q"]
).properties(
    height=280,
    background="#111",
    padding={"left": 10, "right": 10, "top": 10, "bottom": 10}
).configure_view(
    strokeWidth=0
)

st.altair_chart(chart, use_container_width=True)


# ── Data Table ─────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Full Data</div>", unsafe_allow_html=True)

display_df = df_valid[[
    "date", "hrv_ms", "rhr_bpm", "sleep_hours", "sleep_score",
    "strain", "readiness_score", "recommendation"
]].copy()
display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
display_df["readiness_score"] = display_df["readiness_score"].round(1)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "readiness_score": st.column_config.ProgressColumn(
            "Readiness Score",
            min_value=0,
            max_value=100,
            format="%.0f",
        )
    }
)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem; padding-top:1.5rem; border-top:1px solid #1e1e1e;
     color:#444; font-size:0.75rem; text-align:center;">
    Sitting CC Lite — v1.0 · Built by Elijah Mathew ·
    <a href="https://github.com/elijahmathew/sitting-cc-lite" style="color:#555">GitHub</a>
</div>
""", unsafe_allow_html=True)
