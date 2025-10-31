# app.py
"""
Earth 3.0 — Agentic Digital Twin (Demo)
Streamlit MVP (single-file). Uses fake data only (embedded).
Designed for Fortune-500 boards / asset managers: instant index, hotspot map, KPI cards, PDF snapshot.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -------------------------
# Page config & light CSS
# -------------------------
st.set_page_config(page_title="Earth 3.0 — Live Twin (Demo)", layout="wide")
st.markdown("""
<style>
body {color:#0b1726}
.header { font-size:22px; font-weight:700; color:#001F3F; }
.lead { color:#374151; font-size:15px; }
.card { background:#fff; border-radius:12px; padding:14px; box-shadow:0 6px 20px rgba(8,28,50,0.06); }
.kpi { font-size:20px; font-weight:700; color:#001F3F; }
.small { color:#6b7280; }
.alert-red { color: #b91c1c; font-weight:700; }
.alert-green { color: #065f46; font-weight:700; }
.footer { color: #6b7280; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Fake dataset: 6 entities
# -------------------------
def get_fake_orgs():
    # 6 sample orgs with lat/lon and metrics
    data = [
        {"org":"Unilever PLC", "country":"United Kingdom", "lat":51.5074, "lon":-0.1278,
         "Finance":78.0, "AI Governance":85.0, "Climate":62.0, "Equity":71.0, "Sustainability":77.0},
        {"org":"ACME Motors", "country":"USA", "lat":38.9072, "lon":-77.0369,
         "Finance":72.0, "AI Governance":65.0, "Climate":58.0, "Equity":68.0, "Sustainability":60.0},
        {"org":"Nippon Auto", "country":"Japan", "lat":35.6762, "lon":139.6503,
         "Finance":82.0, "AI Governance":88.0, "Climate":74.0, "Equity":79.0, "Sustainability":85.0},
        {"org":"GreenEnergy Ltd", "country":"India", "lat":28.6139, "lon":77.2090,
         "Finance":65.0, "AI Governance":59.0, "Climate":50.0, "Equity":62.0, "Sustainability":55.0},
        {"org":"Continental Foods", "country":"Germany", "lat":52.5200, "lon":13.4050,
         "Finance":83.0, "AI Governance":80.0, "Climate":78.0, "Equity":75.0, "Sustainability":82.0},
        {"org":"GlobalBank", "country":"USA", "lat":40.7128, "lon":-74.0060,
         "Finance":75.0, "AI Governance":55.0, "Climate":68.0, "Equity":66.0, "Sustainability":70.0},
    ]
    df = pd.DataFrame(data)
    # Earth 3.0 Index = average of five metrics
    metric_cols = ["Finance","AI Governance","Climate","Equity","Sustainability"]
    df["Earth3_Index"] = df[metric_cols].mean(axis=1).round(1)
    return df

ORGS_DF = get_fake_orgs()

# -------------------------
# Root header + executive summary
# -------------------------
st.markdown('<div class="header">🌍 Earth 3.0 — Agentic Digital Twin (Demo)</div>', unsafe_allow_html=True)
st.markdown('<div class="lead">Governance that corrects itself — quick board snapshot for CEOs, asset managers, and audit committees.</div>', unsafe_allow_html=True)
st.markdown("---")

# top KPI row: global index, healthy count, alerts
global_index = ORGS_DF["Earth3_Index"].mean().round(1)
num_green = (ORGS_DF["Earth3_Index"] >= 70).sum()
num_red = (ORGS_DF["Earth3_Index"] < 65).sum()

k1, k2, k3, k4 = st.columns([1.5,1,1,1])
with k1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='small'>Earth 3.0 Global Index</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi'>{global_index}%</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'>Average readiness across monitored entities</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with k2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='small'>Healthy Entities (Index ≥ 70)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi' style='color:#065f46'>{num_green}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with k3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='small'>At-risk Entities (Index < 65)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi' style='color:#b91c1c'>{num_red}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with k4:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='small'>Last Updated</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi'>{datetime.utcnow():%b %d %Y}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# Controls & selection
# -------------------------
left, right = st.columns([2,1])
with left:
    st.markdown("### Live Twin Map — Global Hotspots")
    st.markdown("Click 'Show Live Twin' to open the risk hotspot map. Hover markers for quick metrics.")
with right:
    st.markdown("### Controls")
    org_choice = st.selectbox("Select entity (quick view)", options=ORGS_DF["org"].tolist())
    show_map_btn = st.button("🌐 Show Live Twin (Map)")

# -------------------------
# Show map (in-app) when button clicked or always show below selection
# -------------------------
def build_map(df):
    # color: red if Earth3_Index < 65, amber if 65-70, green otherwise
    def status_color(val):
        if val < 65:
            return "red"
        if val < 70:
            return "orange"
        return "green"
    df = df.copy()
    df["status"] = df["Earth3_Index"].apply(lambda v: status_color(v))
    df["text"] = df.apply(lambda r: f"{r['org']} ({r['country']})<br>Earth3 Index: {r['Earth3_Index']}<br>Finance: {r['Finance']} | AI Gov: {r['AI Governance']} | Climate: {r['Climate']}", axis=1)
    fig = px.scatter_geo(df,
                         lat="lat", lon="lon",
                         hover_name="org",
                         hover_data={"country":True, "Earth3_Index":True, "lat":False, "lon":False},
                         color="status",
                         size="Earth3_Index",
                         projection="natural earth",
                         title="")
    fig.update_traces(marker=dict(line=dict(width=0.5, color='rgba(0,0,0,0.15)')))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, legend=dict(title="Status"), height=480)
    return fig

map_shown = False
if show_map_btn:
    map_shown = True

# Also show map if user selects an org and wants to view (makes it discoverable)
if map_shown:
    st.plotly_chart(build_map(ORGS_DF), use_container_width=True)

# -------------------------
# Details panel for selected org
# -------------------------
sel = ORGS_DF[ORGS_DF["org"]==org_choice].iloc[0]

st.markdown("---")
st.markdown(f"## {sel['org']} — Board Dashboard Snapshot")
cols = st.columns([1,1,1,1,1])
metrics = ["Finance","AI Governance","Climate","Equity","Sustainability"]
for c, m in zip(cols, metrics):
    val = sel[m]
    color = "#065f46" if val>=70 else ("#b91c1c" if val<65 else "#b45309")
    with c:
        st.markdown(f"<div class='small'>{m}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:700;color:{color};font-size:18px'>{val}</div>", unsafe_allow_html=True)

st.markdown(f"**Earth 3.0 Index — {sel['Earth3_Index']}**")

# quick actions: download snapshot, show simulated trend
c1, c2 = st.columns([1,2])
with c1:
    if st.button("📄 Download Snapshot (PDF)", key="download_pdf"):
        # prepare text lines
        lines = [
            f"Earth 3.0 — Board Snapshot: {sel['org']}",
            f"Country: {sel['country']}",
            f"Generated: {datetime.utcnow():%B %d, %Y %H:%M UTC}",
            "",
        ]
        for m in metrics:
            lines.append(f"{m}: {sel[m]}")
        lines.append(f"Earth3_Index: {sel['Earth3_Index']}")
        # create PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height-60, f"Earth 3.0 — Board Snapshot: {sel['org']}")
        c.setFont("Helvetica", 10)
        y = height-90
        for ln in lines[1:]:
            c.drawString(40, y, ln)
            y -= 14
        c.showPage()
        c.save()
        buffer.seek(0)
        st.download_button("Download PDF", data=buffer.read(), file_name=f"{sel['org']}_earth3_snapshot.pdf", mime="application/pdf")
with c2:
    st.markdown("### Simulated Trend (12 months)")
    # fake time series for selected org: just use random around its values
    np.random.seed(int(sel["Earth3_Index"]*10))
    months = pd.date_range(end=datetime.utcnow().date(), periods=12, freq='M')
    trend = pd.DataFrame({
        "Date": months,
        "Governance": np.clip(np.linspace(sel["AI Governance"]-6, sel["AI Governance"]+6, 12) + np.random.normal(0,2,12), 0,100).round(1),
        "ESG": np.clip(np.linspace(sel["Sustainability"]-6, sel["Sustainability"]+6, 12) + np.random.normal(0,2,12), 0,100).round(1),
        "Finance": np.clip(np.linspace(sel["Finance"]-6, sel["Finance"]+6, 12) + np.random.normal(0,2,12), 0,100).round(1),
    })
    fig = px.line(trend, x="Date", y=["Governance","ESG","Finance"], labels={"value":"Index", "variable":"Metric"})
    fig.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# -------------------------
# Alerts panel (CEO view)
# -------------------------
st.markdown("---")
st.markdown("### 🔔 Executive Alerts (simulated)")
# alerts: list entities with index < 65 or with AI Governance < 60 or Climate < 60
alerts = []
for _, r in ORGS_DF.iterrows():
    if r["Earth3_Index"] < 65:
        alerts.append((r["org"], "Low overall readiness", f"Index {r['Earth3_Index']}"))
    if r["AI Governance"] < 60:
        alerts.append((r["org"], "AI governance weak", f"AI Gov {r['AI Governance']}"))
    if r["Climate"] < 60:
        alerts.append((r["org"], "Climate resilience low", f"Climate {r['Climate']}"))

if not alerts:
    st.success("No critical alerts detected across monitored entities.")
else:
    for a in alerts:
        st.markdown(f"- **{a[0]}** — {a[1]} ({a[2]})")

# -------------------------
# Bottom: CEO checklist and closing
# -------------------------
st.markdown("---")
st.markdown("## CEO Quick Checklist — What boards will ask in 60s")
st.markdown("""
- **What is our Earth 3.0 Index?** (Top-line readiness for investors & regulators)  
- **Which subsidiaries are red (non-compliant)?** (Map hotspots + audit trails)  
- **How fast can we get a board-pack?** (Download PDF snapshot — ready)  
- **What systems do you connect to?** (ERP, SAP, PLM, Finance — via Agentic RAG)  
""")
st.markdown("<div class='footer'>Demo: This application uses simulated data only. Enterprise integrations require secure Agentic RAG connectors to internal systems.</div>", unsafe_allow_html=True)
