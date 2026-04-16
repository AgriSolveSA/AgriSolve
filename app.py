"""
AgriSolve SME — Multi-Vertical Reconciliation Dashboard
=========================================================
Run:  python -m streamlit run app.py

Select a business vertical from the sidebar. First launch defaults to
Demo data. Upload real CSVs when ready.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from verticals import REGISTRY

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriSolve SME · Reconciliation",
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


# ── Sidebar — vertical selector + data source ─────────────────────────────────
with st.sidebar:
    st.markdown("## AgriSolve SME")
    st.markdown("---")

    vertical_name = st.selectbox("Business vertical", list(REGISTRY.keys()))
    vertical = REGISTRY[vertical_name]()

    st.markdown("---")
    mode = st.radio("Data source", ["Demo data", "Upload CSVs"], index=0)

    labels = vertical.get_upload_labels()
    primary_df: pd.DataFrame | None = None
    secondaries: dict[str, pd.DataFrame] = {}

    if mode == "Demo data":
        st.caption(labels["demo_caption"])
        primary_df, secondaries = vertical.generate_demo()

    else:
        st.markdown(f"**{labels['primary_label']}**")
        reg_file = st.file_uploader(labels["primary_caption"], type="csv", key="reg")
        if reg_file:
            primary_df = pd.read_csv(reg_file)

        st.markdown(f"**{labels['secondary_label']}**")
        stmt_files = st.file_uploader(
            labels["secondary_caption"], type="csv",
            accept_multiple_files=True, key="stmt",
        )
        key_col = labels["secondary_key_column"]
        for f in stmt_files:
            df = pd.read_csv(f)
            if key_col in df.columns and not df.empty:
                secondaries[df[key_col].iloc[0]] = df

    st.markdown("---")
    st.caption(f"AgriSolve SME · {vertical.name} v1.0")


# ── Guard: require data ───────────────────────────────────────────────────────
if primary_df is None or not secondaries:
    st.info("Upload a data file and at least one secondary file to begin.")
    st.stop()


# ── Validation gate ───────────────────────────────────────────────────────────
errors = vertical.validate_inputs(primary_df, secondaries)
for err in errors:
    st.error(err)
if errors:
    st.stop()


# ── Compute ───────────────────────────────────────────────────────────────────
exceptions_df  = vertical.run_reconciliation(primary_df, secondaries)
stats          = vertical.get_summary_stats(primary_df, secondaries, exceptions_df)
entity_summary = vertical.get_entity_summary(primary_df, secondaries)


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
    st.subheader(f"March 2026 — {vertical.name} Summary")

    # KPI cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric(stats["kpi1_label"], stats["kpi1_value"])
    c2.metric(stats["kpi2_label"], stats["kpi2_value"])
    c3.metric(
        stats["kpi3_label"],
        stats["kpi3_value"],
        delta=stats["kpi3_delta"],
        delta_color="normal" if stats["kpi3_positive"] else "inverse",
    )
    c4.metric(stats["kpi4_label"], stats["kpi4_value"])
    c5.metric(stats["kpi5_label"], stats["kpi5_value"])
    c6.metric(stats["kpi6_label"], stats["kpi6_value"])

    st.markdown("&nbsp;")

    # Grouped bar — expected vs received per counterparty
    fig = go.Figure(data=[
        go.Bar(
            name="Expected",
            x=entity_summary["entity"],
            y=entity_summary["expected"],
            marker_color="#7c3aed",
            text=[f"R {v:,.0f}" for v in entity_summary["expected"]],
            textposition="outside",
        ),
        go.Bar(
            name="Received",
            x=entity_summary["entity"],
            y=entity_summary["actual"],
            marker_color="#06b6d4",
            text=[f"R {v:,.0f}" for v in entity_summary["actual"]],
            textposition="outside",
        ),
    ])
    fig.update_layout(
        title=f"Expected vs Received — by {vertical.counterparty_label}",
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

    # Exception breakdown charts
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
            cp_exc = (
                exceptions_df
                .groupby("counterparty")["variance"]
                .apply(lambda s: s.abs().sum())
                .reset_index()
                .rename(columns={"variance": "total_at_risk"})
                .sort_values("total_at_risk", ascending=False)
            )
            bar2 = px.bar(
                cp_exc, x="counterparty", y="total_at_risk",
                title=f"Total Variance at Risk by {vertical.counterparty_label}",
                color="total_at_risk",
                color_continuous_scale="Purpor",
                labels={"counterparty": "", "total_at_risk": "Amount (R)"},
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
        st.success("No exceptions found. All records reconcile within tolerance.")
        st.stop()

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    cp_options   = ["All"] + sorted(exceptions_df["counterparty"].unique().tolist())
    type_options = ["All"] + sorted(exceptions_df["exception_type"].unique().tolist())
    sev_options  = ["All", "High", "Medium", "Low"]

    sel_cp   = fc1.selectbox(vertical.counterparty_label, cp_options)
    sel_type = fc2.selectbox("Exception type",           type_options)
    sel_sev  = fc3.selectbox("Severity",                 sev_options)

    filtered = exceptions_df.copy()
    if sel_cp   != "All": filtered = filtered[filtered["counterparty"]   == sel_cp]
    if sel_type != "All": filtered = filtered[filtered["exception_type"] == sel_type]
    if sel_sev  != "All": filtered = filtered[filtered["severity"]       == sel_sev]

    total_at_risk = filtered["variance"].abs().sum()
    st.caption(
        f"Showing {len(filtered)} exception(s) · "
        f"Total at risk: **R {total_at_risk:,.2f}**"
    )

    # Standard columns always present; optional extras shown if available
    standard_cols = ["counterparty", "entity_id", "description",
                     "exception_type", "severity", "variance"]
    extra_cols = [c for c in ["product_type", "policy_status", "expected", "actual"]
                  if c in filtered.columns]
    display_cols = standard_cols + extra_cols

    col_labels = {
        "counterparty":   vertical.counterparty_label,
        "entity_id":      vertical.primary_entity_label + " #",
        "description":    "Client / Subject",
        "product_type":   "Product",
        "policy_status":  "Status",
        "expected":       "Expected (R)",
        "actual":         "Received (R)",
        "variance":       "Variance (R)",
        "exception_type": "Exception",
        "severity":       "Severity",
    }

    def colour_severity(val: str) -> str:
        colours = {"High": "background-color:#4a1a1a", "Medium": "background-color:#3d2f0a"}
        return colours.get(val, "")

    fmt: dict[str, str] = {"Variance (R)": "R {:,.2f}"}
    if "expected" in extra_cols:
        fmt["Expected (R)"] = "R {:,.2f}"
    if "actual" in extra_cols:
        fmt["Received (R)"] = "R {:,.2f}"

    styled = (
        filtered[display_cols]
        .rename(columns=col_labels)
        .style
        .map(colour_severity, subset=["Severity"])
        .format(fmt)
    )
    st.dataframe(styled, use_container_width=True, height=500)

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

    rt = vertical.get_recovery_tracker_label()

    st.markdown(f"#### {rt['prior_section']}")
    kc1, kc2, kc3 = st.columns(3)
    kc1.metric(rt["disputed_label"],  rt["disputed_value"])
    kc2.metric(rt["recovered_label"], rt["recovered_value"], delta=rt["recovered_delta"])
    kc3.metric(rt["pending_label"],   rt["pending_value"])
    st.dataframe(pd.DataFrame(rt["prior_rows"]), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"#### {rt['current_section']}")

    if exceptions_df.empty:
        st.success("No new exceptions to track.")
    else:
        queue_cols = ["counterparty", "entity_id", "description",
                      "exception_type", "variance", "severity"]
        queue = exceptions_df[queue_cols].copy()
        queue["dispute_status"] = "To Dispute"
        queue["variance_abs"]   = queue["variance"].abs().round(2)

        cp_col  = vertical.counterparty_label
        ent_col = vertical.primary_entity_label + " #"

        queue_display = queue.rename(columns={
            "counterparty":   cp_col,
            "entity_id":      ent_col,
            "description":    "Client / Subject",
            "exception_type": "Exception",
            "variance_abs":   "Amount (R)",
            "severity":       "Priority",
            "dispute_status": "Status",
        })[[cp_col, ent_col, "Client / Subject", "Exception", "Amount (R)", "Priority", "Status"]]

        total_queue = queue["variance_abs"].sum()
        st.caption(
            f"{len(queue)} {rt['entity_noun']} to dispute · "
            f"Total: **R {total_queue:,.2f}**"
        )
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
            f"Raise these {len(queue)} disputes with your {rt['counterparty_noun']} "
            f"this week. At a 60% recovery rate, expect "
            f"**R {total_queue * 0.6:,.0f}** back next month."
        )
