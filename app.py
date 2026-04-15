"""
Commission Reconciliation Dashboard
====================================
Run:  streamlit run app.py

First launch uses built-in demo data (240 policies, 3 insurers, 8 discrepancies).
Use the sidebar to upload real client data when ready.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

from generate_demo_data import generate_demo
from reconcile import reconcile, summary_stats, insurer_summary

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Commission Reconciliation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* KPI cards */
[data-testid="metric-container"] {
    background: #1e1e2e;
    border: 1px solid #2d2d3f;
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.78rem;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f7fafc;
}

/* Sidebar header */
section[data-testid="stSidebar"] h2 { color: #7c3aed; }

/* Exception type badges rendered as text */
.badge-high    { color: #fc8181; font-weight: 600; }
.badge-medium  { color: #f6ad55; font-weight: 600; }
.badge-low     { color: #68d391; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar — data source ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Commission Recon")
    st.markdown("---")
    mode = st.radio("Data source", ["Demo data", "Upload CSVs"], index=0)

    register_df: pd.DataFrame | None = None
    statements: dict[str, pd.DataFrame] = {}

    if mode == "Demo data":
        st.caption("240 policies · 3 insurers · 8 seeded discrepancies")
        register_df, statements = generate_demo()

    else:
        st.markdown("**Policy Register**")
        reg_file = st.file_uploader("Upload register CSV", type="csv", key="reg")
        if reg_file:
            register_df = pd.read_csv(reg_file)

        st.markdown("**Commission Statements**")
        stmt_files = st.file_uploader(
            "Upload one CSV per insurer", type="csv",
            accept_multiple_files=True, key="stmt"
        )
        for f in stmt_files:
            df = pd.read_csv(f)
            if "insurer_name" in df.columns and not df.empty:
                insurer = df["insurer_name"].iloc[0]
                statements[insurer] = df

    st.markdown("---")
    st.caption("Vantix SME · Commission Recon v1.0")


# ── Guard: require data ───────────────────────────────────────────────────────
if register_df is None or not statements:
    st.info("Upload a policy register and at least one commission statement to begin.")
    st.stop()


# ── Compute ───────────────────────────────────────────────────────────────────
exceptions_df = reconcile(register_df, statements)
stats         = summary_stats(register_df, statements, exceptions_df)
ins_summary   = insurer_summary(register_df, statements)


# ── Navigation ────────────────────────────────────────────────────────────────
page = st.radio(
    "View",
    ["Overview", "Exception Report", "Recovery Tracker"],
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.subheader("March 2026 — Commission Summary")

    # KPI cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Expected", f"R {stats['total_expected']:,.0f}")
    c2.metric("Received", f"R {stats['total_actual']:,.0f}")

    var = stats["total_variance"]
    c3.metric(
        "Net Variance",
        f"R {abs(var):,.0f}",
        delta=f"{'▲' if var >= 0 else '▼'} {'surplus' if var >= 0 else 'shortfall'}",
        delta_color="normal" if var >= 0 else "inverse",
    )
    c4.metric("Exceptions", stats["exception_count"])
    c5.metric("High Priority", stats["high_count"])
    c6.metric("Total at Risk", f"R {stats['total_at_risk']:,.0f}")

    st.markdown("&nbsp;")

    # Commission waterfall — grouped bar per insurer
    fig = go.Figure(data=[
        go.Bar(
            name="Expected",
            x=ins_summary["insurer"],
            y=ins_summary["expected"],
            marker_color="#7c3aed",
            text=[f"R {v:,.0f}" for v in ins_summary["expected"]],
            textposition="outside",
        ),
        go.Bar(
            name="Received",
            x=ins_summary["insurer"],
            y=ins_summary["actual"],
            marker_color="#06b6d4",
            text=[f"R {v:,.0f}" for v in ins_summary["actual"]],
            textposition="outside",
        ),
    ])
    fig.update_layout(
        title="Expected vs Received Commission by Insurer",
        barmode="group",
        plot_bgcolor="#0f0f1a",
        paper_bgcolor="#0f0f1a",
        font_color="#e2e8f0",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40, l=10, r=10),
        height=400,
    )
    fig.update_yaxes(tickprefix="R ", gridcolor="#2d2d3f")
    fig.update_xaxes(gridcolor="#2d2d3f")
    st.plotly_chart(fig, use_container_width=True)

    # Exception breakdown pie
    if not exceptions_df.empty:
        col_a, col_b = st.columns(2)

        with col_a:
            type_counts = exceptions_df["exception_type"].value_counts().reset_index()
            type_counts.columns = ["type", "count"]
            pie = px.pie(
                type_counts, names="type", values="count",
                title="Exceptions by Type",
                color_discrete_sequence=px.colors.sequential.Purpor,
            )
            pie.update_layout(
                plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
                font_color="#e2e8f0", height=320,
            )
            st.plotly_chart(pie, use_container_width=True)

        with col_b:
            ins_exc = (
                exceptions_df
                .groupby("insurer_name")["variance"]
                .apply(lambda s: s.abs().sum())
                .reset_index()
                .rename(columns={"variance": "total_at_risk"})
                .sort_values("total_at_risk", ascending=False)
            )
            bar2 = px.bar(
                ins_exc, x="insurer_name", y="total_at_risk",
                title="Total Variance at Risk by Insurer",
                color="total_at_risk",
                color_continuous_scale="Purpor",
                labels={"insurer_name": "", "total_at_risk": "Amount (R)"},
            )
            bar2.update_layout(
                plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
                font_color="#e2e8f0", height=320, showlegend=False,
                coloraxis_showscale=False,
            )
            bar2.update_yaxes(tickprefix="R ", gridcolor="#2d2d3f")
            st.plotly_chart(bar2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: EXCEPTION REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Exception Report":
    st.subheader(f"Exception Report — {len(exceptions_df)} items found")

    if exceptions_df.empty:
        st.success("No exceptions found. All commissions reconcile within tolerance.")
        st.stop()

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    insurers_available = ["All"] + sorted(exceptions_df["insurer_name"].unique().tolist())
    types_available    = ["All"] + sorted(exceptions_df["exception_type"].unique().tolist())
    sev_available      = ["All"] + ["High", "Medium", "Low"]

    sel_ins  = fc1.selectbox("Insurer",        insurers_available)
    sel_type = fc2.selectbox("Exception type", types_available)
    sel_sev  = fc3.selectbox("Severity",       sev_available)

    filtered = exceptions_df.copy()
    if sel_ins  != "All": filtered = filtered[filtered["insurer_name"]   == sel_ins]
    if sel_type != "All": filtered = filtered[filtered["exception_type"] == sel_type]
    if sel_sev  != "All": filtered = filtered[filtered["severity"]       == sel_sev]

    # Summary row
    total_at_risk = filtered["variance"].abs().sum()
    st.caption(
        f"Showing {len(filtered)} exception(s) · "
        f"Total at risk: **R {total_at_risk:,.2f}**"
    )

    # Colour-map severity
    def colour_severity(val: str) -> str:
        colours = {"High": "background-color:#4a1a1a", "Medium": "background-color:#3d2f0a"}
        return colours.get(val, "")

    display_cols = [
        "insurer_name", "policy_number", "client", "product_type",
        "policy_status", "expected", "actual", "variance",
        "exception_type", "severity",
    ]
    display_labels = {
        "insurer_name":   "Insurer",
        "policy_number":  "Policy #",
        "client":         "Client",
        "product_type":   "Product",
        "policy_status":  "Status",
        "expected":       "Expected (R)",
        "actual":         "Received (R)",
        "variance":       "Variance (R)",
        "exception_type": "Exception",
        "severity":       "Severity",
    }

    styled = (
        filtered[display_cols]
        .rename(columns=display_labels)
        .style
        .map(colour_severity, subset=["Severity"])
        .format({
            "Expected (R)":  "R {:,.2f}",
            "Received (R)":  "R {:,.2f}",
            "Variance (R)":  "R {:,.2f}",
        })
    )
    st.dataframe(styled, use_container_width=True, height=500)

    # Export
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download exceptions CSV",
        data=csv,
        file_name="exceptions_2026_03.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: RECOVERY TRACKER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Recovery Tracker":
    st.subheader("Recovery Tracker")

    # Simulated prior-month recovery (demo story: tool has been running 1 month)
    prior = pd.DataFrame([
        {"Policy #": "POL-1102", "Insurer": "Pinnacle Life Insurance",
         "Disputed": "R 4,200", "Status": "Recovered", "Recovered": "R 4,200", "Notes": "Insurer confirmed error"},
        {"Policy #": "POL-2045", "Insurer": "Meridian Short-Term",
         "Disputed": "R 1,950", "Status": "Recovered", "Recovered": "R 1,950", "Notes": "Rate correction applied"},
        {"Policy #": "POL-3019", "Insurer": "Apex Financial Services",
         "Disputed": "R 3,100", "Status": "In Dispute", "Recovered": "—", "Notes": "Awaiting insurer response"},
    ])

    st.markdown("#### Prior Month — February 2026")
    kc1, kc2, kc3 = st.columns(3)
    kc1.metric("Disputed",  "R 9,250")
    kc2.metric("Recovered", "R 6,150",  delta="66% recovery rate")
    kc3.metric("Pending",   "R 3,100")
    st.dataframe(prior, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### Current Month — March 2026 (New Exceptions)")

    if exceptions_df.empty:
        st.success("No new exceptions to track.")
    else:
        queue = exceptions_df[[
            "insurer_name", "policy_number", "client",
            "exception_type", "variance", "severity"
        ]].copy()
        queue["dispute_status"] = "To Dispute"
        queue["variance_abs"]   = queue["variance"].abs().round(2)

        queue_display = queue.rename(columns={
            "insurer_name":   "Insurer",
            "policy_number":  "Policy #",
            "client":         "Client",
            "exception_type": "Exception",
            "variance_abs":   "Amount (R)",
            "severity":       "Priority",
            "dispute_status": "Status",
        })[["Insurer", "Policy #", "Client", "Exception", "Amount (R)", "Priority", "Status"]]

        total_queue = queue["variance_abs"].sum()
        st.caption(f"{len(queue)} exceptions to dispute · Total: **R {total_queue:,.2f}**")
        st.dataframe(
            queue_display.style.format({"Amount (R)": "R {:,.2f}"}),
            use_container_width=True,
            hide_index=True,
            height=420,
        )

        csv_q = queue_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Export dispute queue",
            data=csv_q,
            file_name="dispute_queue_2026_03.csv",
            mime="text/csv",
        )

        st.info(
            f"Raise these {len(queue)} disputes with your insurers this week. "
            f"At a 60% recovery rate, expect **R {total_queue * 0.6:,.0f}** back next month."
        )
