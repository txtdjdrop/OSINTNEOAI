"""
OSINT Neo AI - Investigation Dashboard
Streamlit app for HBNC investigation data, breach analysis, grant tracking, and GIS exploration
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="OSINT Neo AI - Investigation Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# THEME TOGGLE
# =============================================================================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

IS_DARK = st.session_state.theme == "dark"

# =============================================================================
# CSS DESIGN SYSTEM
# =============================================================================
bg = "#09090b" if IS_DARK else "#ffffff"
bg_subtle = "#0c0c0f" if IS_DARK else "#f9fafb"
card = "#0c0c0f" if IS_DARK else "#ffffff"
card_hover = "#131316" if IS_DARK else "#f4f4f5"
border = "#1e1e24" if IS_DARK else "#e4e4e7"
border_subtle = "#16161a" if IS_DARK else "#f0f0f2"
text = "#fafafa" if IS_DARK else "#09090b"
text_muted = "#71717a"
text_dim = "#52525b" if IS_DARK else "#a1a1aa"
accent = "#2563eb"
green = "#22c55e" if IS_DARK else "#16a34a"
green_muted = "rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)"
red = "#ef4444" if IS_DARK else "#dc2626"
red_muted = "rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)"
amber = "#f59e0b" if IS_DARK else "#d97706"
amber_muted = "rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)"
shadow = "none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"
radius = "10px"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --bg: {bg};
    --bg-subtle: {bg_subtle};
    --card: {card};
    --card-hover: {card_hover};
    --border: {border};
    --border-subtle: {border_subtle};
    --text: {text};
    --text-muted: {text_muted};
    --text-dim: {text_dim};
    --accent: {accent};
    --green: {green};
    --green-muted: {green_muted};
    --red: {red};
    --red-muted: {red_muted};
    --amber: {amber};
    --amber-muted: {amber_muted};
    --shadow: {shadow};
    --radius: {radius};
}}

header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}
.block-container {{
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1360px !important;
}}

button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.835rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1rem !important;
    border: 1px solid transparent !important;
    border-radius: 7px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--text) !important;
    background: var(--card) !important;
    border-color: var(--border) !important;
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
    display: none !important;
}}
[data-baseweb="tab-list"] {{
    gap: 4px !important;
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 3px;
}}

.metric-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow);
}}
.metric-label {{
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 500;
}}
.metric-value {{
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
}}
.metric-delta {{
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.4rem;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
}}
.delta-up {{ color: var(--green); background: var(--green-muted); }}
.delta-down {{ color: var(--red); background: var(--red-muted); }}
.delta-warn {{ color: var(--amber); background: var(--amber-muted); }}

.chart-wrap {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.2rem 0.6rem;
    box-shadow: var(--shadow);
}}
.chart-title {{
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text);
}}
.chart-subtitle {{
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-bottom: 0.8rem;
}}

.data-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.8rem;
}}
.data-table th {{
    text-align: left;
    padding: 0.6rem 0.8rem;
    color: var(--text-muted);
    font-weight: 500;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border);
}}
.data-table td {{
    padding: 0.65rem 0.8rem;
    color: var(--text);
    border-bottom: 1px solid var(--border-subtle);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
}}
.data-table tr:last-child td {{
    border-bottom: none;
}}

.badge {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 500;
}}
.badge-green {{ color: var(--green); background: var(--green-muted); }}
.badge-red {{ color: var(--red); background: var(--red-muted); }}
.badge-amber {{ color: var(--amber); background: var(--amber-muted); }}
.badge-blue {{ color: var(--accent); background: rgba(37,99,235,0.1); }}

.brand {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.brand-name {{
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.02em;
}}
.brand-icon {{
    width: 28px;
    height: 28px;
    background: var(--accent);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 0.8rem;
}}

[data-testid="stHorizontalBlock"] {{ gap: 1.25rem !important; }}
[data-testid="stVerticalBlock"] > div:has(> [data-testid="stHorizontalBlock"]) {{
    margin-bottom: 0.5rem !important;
}}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def metric_card(label, value, delta=None, delta_type="up"):
    cls = f"delta-{delta_type}"
    arrow = "↑" if delta_type == "up" else ("↓" if delta_type == "down" else "→")
    delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def chart_header(title, subtitle=""):
    st.markdown(f"""
    <div class="chart-wrap">
        <div class="chart-title">{title}</div>
        <div class="chart-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)

def chart_footer():
    st.markdown("</div>", unsafe_allow_html=True)

def badge(text, color="blue"):
    return f'<span class="badge badge-{color}">{text}</span>'

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#71717a" if not IS_DARK else "#a1a1aa", size=11),
    margin=dict(l=0, r=0, t=8, b=0),
    xaxis=dict(
        gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
        zerolinecolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
        tickfont=dict(size=10, color="#71717a"),
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
        zerolinecolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
        tickfont=dict(size=10, color="#71717a"),
    ),
)

# =============================================================================
# LOAD DATA
# =============================================================================
DATA_DIR = Path(__file__).parent.parent / "data" / "huntington_beach"

@st.cache_data
def load_breach_data():
    try:
        with open(DATA_DIR / "breach_check_results.json") as f:
            return json.load(f)
    except:
        return {"emails": {}, "total": 0, "compromised": 0}

@st.cache_data
def load_grants_data():
    try:
        grants_path = Path(__file__).parent.parent / "data" / "taxfunded_grants_ingestion.json"
        with open(grants_path) as f:
            return json.load(f)
    except:
        return {"grants": [], "total_grants_tracked": 0, "total_disbursed_usd": 0}

@st.cache_data
def load_gis_datasets():
    datasets = []
    for f in DATA_DIR.glob("*.json"):
        if f.name not in ["breach_check_results.json", "service_urls.json"]:
            size_mb = f.stat().st_size / (1024 * 1024)
            name = f.stem.replace("HB_", "").replace("_", " ")
            datasets.append({"name": name, "file": f.name, "size_mb": round(size_mb, 2)})
    return pd.DataFrame(datasets)

breach_data = load_breach_data()
grants_data = load_grants_data()
gis_df = load_gis_datasets()

# =============================================================================
# HEADER
# =============================================================================
head_left, head_right = st.columns([8, 1])
with head_left:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">◆</div>
        <span class="brand-name">OSINT Neo AI — Investigation Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

# =============================================================================
# TABS
# =============================================================================
tab_overview, tab_breaches, tab_grants, tab_gis, tab_txf, tab_chat = st.tabs([
    "📊 Overview", "🔓 Breach Analysis", "💰 Grant Tracking", "🗺️ GIS Explorer", "⛓️ TXF Ledger", "💬 Chat"
])

# =============================================================================
# TAB: OVERVIEW
# =============================================================================
with tab_overview:
    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Total Emails", "53", delta="All entities mapped", delta_type="up")
    with c2:
        metric_card("Compromised", "5", delta="9.4% breach rate", delta_type="down")
    with c3:
        metric_card("Grants Tracked", str(grants_data.get("total_grants_tracked", 12)),
                     delta=f"${grants_data.get('total_disbursed_usd', 0)/1e6:.1f}M total", delta_type="up")
    with c4:
        metric_card("GIS Datasets", str(len(gis_df)), delta="HB layers loaded", delta_type="up")
    with c5:
        metric_card("TXF Ledger", "6 Blocks", delta="168.8M TXF supply", delta_type="up")

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # Investigation Summary
    col_left, col_right = st.columns([2, 1])

    with col_left:
        chart_header("Investigation Scope", "HBNC at 17642 Beach Blvd / 17631 Cameron Ln")
        st.markdown(f"""
        <div style="padding: 0.5rem 0; color: var(--text); font-size: 0.82rem; line-height: 1.6;">
        <strong>Target:</strong> Huntington Beach Navigation Center (HBNC)<br>
        <strong>Operator:</strong> Mercy House Living Centers<br>
        <strong>Capacity:</strong> 174-bed emergency shelter<br>
        <strong>Total Investment:</strong> $8.2M+ (City of Huntington Beach)<br>
        <strong>Zoning:</strong> SP14 (Specific Plan 14) | Tract: tr405<br>
        <strong>Soil:</strong> Loamy Sand | <strong>Flood:</strong> Zone X (reduced risk)<br>
        <strong>Subsidence:</strong> Active zone (0 to -0.1 ft ground sinking)<br>
        <strong>Utility:</strong> SCE 12kV primary underground (1970 easement)<br>
        <strong>Oil Wells:</strong> 1 within 1km radius<br>
        <strong>Fault Zone:</strong> Within 5km of fault center
        </div>
        """, unsafe_allow_html=True)
        chart_footer()

    with col_right:
        chart_header("Entity Contacts by Domain", "53 emails across 5 domains")
        domains = {}
        for email, data in breach_data.get("emails", {}).items():
            domain = email.split("@")[1] if "@" in email else "unknown"
            domains[domain] = domains.get(domain, 0) + 1
        fig_domains = px.pie(
            values=list(domains.values()),
            names=list(domains.keys()),
            hole=0.5,
            color_discrete_sequence=["#2563eb", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"]
        )
        fig_domains.update_layout(**PLOT_LAYOUT, height=220, showlegend=True,
                                   legend=dict(font=dict(size=10), x=0.5, y=0.5, xanchor="center"))
        st.plotly_chart(fig_domains, use_container_width=True, config={"displayModeBar": False})
        chart_footer()

# =============================================================================
# TAB: BREACH ANALYSIS
# =============================================================================
with tab_breaches:
    st.markdown("### 🔓 Email Breach Analysis")

    # Breach summary
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Total Scanned", str(breach_data.get("total", 53)))
    with c2:
        metric_card("Compromised", str(breach_data.get("compromised", 5)), delta_type="down")
    with c3:
        safe = breach_data.get("total", 53) - breach_data.get("compromised", 5) - breach_data.get("errors", 48)
        metric_card("Safe", str(safe), delta_type="up")

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # Compromised accounts table
    chart_header("Compromised Accounts Detail", "Accounts found in data breaches")
    compromised = []
    for email, data in breach_data.get("emails", {}).items():
        if data.get("status") == "COMPROMISED":
            sources = data.get("sources", [])
            source_names = ", ".join([s.get("name", "") for s in sources])
            dates = ", ".join([s.get("date", "") for s in sources])
            compromised.append({
                "Email": email,
                "Breaches": data.get("found", 0),
                "Sources": source_names,
                "Dates": dates,
                "Risk": "CRITICAL" if data.get("found", 0) >= 5 else "HIGH"
            })

    if compromised:
        df_comp = pd.DataFrame(compromised)
        rows_html = ""
        for _, row in df_comp.iterrows():
            risk_color = "red" if row["Risk"] == "CRITICAL" else "amber"
            rows_html += f"""
            <tr>
                <td>{row["Email"]}</td>
                <td>{row["Breaches"]}</td>
                <td>{row["Sources"]}</td>
                <td>{row["Dates"]}</td>
                <td>{badge(row["Risk"], risk_color)}</td>
            </tr>
            """
        st.markdown(f"""
        <table class="data-table">
            <thead><tr><th>Email</th><th>Breaches</th><th>Sources</th><th>Dates</th><th>Risk</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)
    chart_footer()

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # Breach timeline
    chart_header("Breach Timeline", "When accounts were compromised")
    breach_timeline = []
    for email, data in breach_data.get("emails", {}).items():
        if data.get("status") == "COMPROMISED":
            for source in data.get("sources", []):
                breach_timeline.append({
                    "Email": email.split("@")[0],
                    "Source": source.get("name", ""),
                    "Date": source.get("date", ""),
                    "Breaches": data.get("found", 0)
                })

    if breach_timeline:
        df_timeline = pd.DataFrame(breach_timeline)
        fig_timeline = px.scatter(
            df_timeline, x="Date", y="Email", size="Breaches",
            color="Source", hover_data=["Source"],
            color_discrete_sequence=["#2563eb", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"]
        )
        fig_timeline.update_layout(**PLOT_LAYOUT, height=300)
        st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
    chart_footer()

# =============================================================================
# TAB: GRANT TRACKING
# =============================================================================
with tab_grants:
    st.markdown("### 💰 Taxpayer-Funded Grant Tracking")

    grants = grants_data.get("grants", [])

    # KPI Row
    total_amount = sum(g.get("amount_usd", 0) for g in grants)
    flagged = len([g for g in grants if "FLAGGED" in g.get("status", "")])
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Total Grants", str(len(grants)), delta=f"${total_amount/1e6:.1f}M tracked", delta_type="up")
    with c2:
        metric_card("Flagged for Audit", str(flagged), delta="FCA/CEQA/RICO", delta_type="down")
    with c3:
        verified = len([g for g in grants if "VERIFIED" in g.get("status", "")])
        metric_card("Verified", str(verified), delta_type="up")

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        chart_header("Grants by Amount", "Top 10 grants by USD value")
        df_grants = pd.DataFrame(grants)
        df_grants = df_grants.sort_values("amount_usd", ascending=True).tail(10)
        fig_grants = px.bar(
            df_grants, x="amount_usd", y="recipient_name",
            orientation="h",
            color="status",
            color_discrete_map={
                "FLAGGED_FOR_FCA_RICO_AUDIT": "#ef4444",
                "FLAGGED_FOR_CEQA_TOXIC_PLUME_EVASION": "#f59e0b",
                "VERIFIED_USASPENDING_AWARD": "#22c55e",
                "VERIFIED_CA_GRANTS_PORTAL": "#2563eb"
            }
        )
        fig_grants.update_layout(**PLOT_LAYOUT, height=400, showlegend=True,
                                  legend=dict(font=dict(size=9), orientation="h", y=1.1))
        fig_grants.update_traces(texttemplate="$%{x:,.0f}", textposition="outside")
        st.plotly_chart(fig_grants, use_container_width=True, config={"displayModeBar": False})
        chart_footer()

    with col_table:
        chart_header("Grant Details", "All tracked grants")
        rows_html = ""
        for g in grants:
            status = g.get("status", "")
            if "FLAGGED" in status:
                status_badge = badge("FLAGGED", "red")
            else:
                status_badge = badge("VERIFIED", "green")
            rows_html += f"""
            <tr>
                <td style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{g.get("recipient_name", "")[:30]}</td>
                <td>${g.get("amount_usd", 0):,.0f}</td>
                <td>{g.get("funding_agency", "")[:25]}</td>
                <td>{status_badge}</td>
            </tr>
            """
        st.markdown(f"""
        <table class="data-table">
            <thead><tr><th>Recipient</th><th>Amount</th><th>Agency</th><th>Status</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)
        chart_footer()

# =============================================================================
# TAB: GIS EXPLORER
# =============================================================================
with tab_gis:
    st.markdown("### 🗺️ Huntington Beach GIS Data Explorer")

    chart_header("Available GIS Datasets", "15 layers from HB ArcGIS Hub")
    fig_gis = px.bar(
        gis_df.sort_values("size_mb", ascending=True),
        x="size_mb", y="name",
        orientation="h",
        color="size_mb",
        color_continuous_scale=["#2563eb", "#22c55e", "#f59e0b", "#ef4444"]
    )
    fig_gis.update_layout(**PLOT_LAYOUT, height=450, showlegend=False,
                           coloraxis_showscale=False)
    fig_gis.update_traces(texttemplate="%{x:.1f} MB", textposition="outside")
    st.plotly_chart(fig_gis, use_container_width=True, config={"displayModeBar": False})
    chart_footer()

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # Dataset details
    chart_header("Dataset Catalog", "File details and service endpoints")
    rows_html = ""
    for _, row in gis_df.iterrows():
        rows_html += f"""
        <tr>
            <td>{row["name"]}</td>
            <td>{row["file"]}</td>
            <td>{row["size_mb"]:.2f} MB</td>
        </tr>
        """
    st.markdown(f"""
    <table class="data-table">
        <thead><tr><th>Dataset</th><th>Filename</th><th>Size</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    chart_footer()

# =============================================================================
# TAB: TXF LEDGER
# =============================================================================
with tab_txf:
    st.markdown("### ⛓️ TaxFunded Token Ledger")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Supply", "168,810,675", delta="TXF tokens", delta_type="up")
    with c2:
        metric_card("Blocks", "6", delta="Chain height", delta_type="up")
    with c3:
        metric_card("Transactions", "9", delta="All time", delta_type="up")
    with c4:
        metric_card("Grant Awards", "5", delta="Tracked on-chain", delta_type="up")

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    chart_header("TXF Token Flow", "Minting and transfer history")
    txf_data = {
        "Event": ["Genesis Block", "LAHSA Award", "Abode Award", "PATH Award",
                  "Mercy House Award", "Jamboree Award"],
        "Amount": [142500000, 14250000, 12100000, 8400000, 2600000, 3200000],
        "Type": ["Mint", "Transfer", "Transfer", "Transfer", "Transfer", "Transfer"]
    }
    df_txf = pd.DataFrame(txf_data)
    fig_txf = px.bar(
        df_txf, x="Event", y="Amount", color="Type",
        color_discrete_map={"Mint": "#2563eb", "Transfer": "#22c55e"}
    )
    fig_txf.update_layout(**PLOT_LAYOUT, height=350)
    fig_txf.update_traces(texttemplate="$%{y:,.0f}", textposition="outside")
    st.plotly_chart(fig_txf, use_container_width=True, config={"displayModeBar": False})
    chart_footer()

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    chart_header("Grant Recipients on Ledger", "Taxpayer-funded awards tracked via TXF tokens")
    recipients = [
        {"Recipient": "LAHSA", "Amount": "$142.5M", "Status": "FLAGGED", "Type": "Homeless Services"},
        {"Recipient": "Abode Services", "Amount": "$12.1M", "Status": "FLAGGED", "Type": "Housing"},
        {"Recipient": "PATH (People Assisting The Homeless)", "Amount": "$8.4M", "Status": "FLAGGED", "Type": "Housing"},
        {"Recipient": "Mercy House Living Centers", "Amount": "$2.6M", "Status": "FLAGGED", "Type": "Shelter Operations"},
        {"Recipient": "Jamboree Housing", "Amount": "$3.2M", "Status": "VERIFIED", "Type": "Affordable Housing"},
    ]
    rows_html = ""
    for r in recipients:
        status_badge = badge(r["Status"], "red" if r["Status"] == "FLAGGED" else "green")
        rows_html += f"""
        <tr>
            <td>{r["Recipient"]}</td>
            <td>{r["Amount"]}</td>
            <td>{status_badge}</td>
            <td>{r["Type"]}</td>
        </tr>
        """
    st.markdown(f"""
    <table class="data-table">
        <thead><tr><th>Recipient</th><th>Amount</th><th>Status</th><th>Type</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    chart_footer()

# =============================================================================
# TAB: CHAT
# =============================================================================
with tab_chat:
    st.markdown("### 💬 OSINT Chat Assistant")
    st.markdown("""
    <div style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 1rem;">
    Ask natural language questions about the investigation data. Powered by Gemini Data Analytics with BigQuery backend.
    </div>
    """, unsafe_allow_html=True)
    
    # Import and render chat interface
    try:
        from chat_interface import render_chat_panel
        render_chat_panel(IS_DARK)
    except ImportError:
        st.error("Chat interface module not found. Make sure chat_interface.py is in the gui directory.")
    except Exception as e:
        st.error(f"Chat interface error: {str(e)}")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: var(--text-dim); font-size: 0.72rem;">
    OSINT Neo AI — Taxpayer-Funded Investigation Dashboard | Data as of {datetime.now().strftime("%B %d, %Y")} | 
    Powered by Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
