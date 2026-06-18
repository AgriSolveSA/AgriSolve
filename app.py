"""
AgriSolve SME — Multi-Vertical Reconciliation Dashboard
=========================================================
Run:  python -m streamlit run app.py

Features:
- Multi-vertical: Insurance Broker, Accounting, Construction, Logistics
- Demo data or CSV upload per vertical
- Period selector (any month/year)
- Exception report with severity filtering
- Recovery tracker with dispute queue
- Excel export (Summary + Exceptions + Recovery sheets)
- Email digest via SMTP (configured in .streamlit/secrets.toml)
"""

import io
import smtplib
import calendar
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from verticals import REGISTRY
from auth import authenticate, allowed_verticals

# ── Page config (must be the very first Streamlit command — st.text_input
#    in the old auth gate ran before this, which raises StreamlitAPIException
#    the moment a real password is configured; hidden until now because no
#    deployment has ever had dashboard_password set in this dev/demo env) ──
st.set_page_config(
    page_title="AgriSolve SME · Reconciliation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth gate ─────────────────────────────────────────────────────────────────
# Per-client passwords (st.secrets["clients"]) restrict each client to their
# own vertical(s); the legacy single dashboard_password still works for
# anyone not yet migrated, with no restriction (sees every vertical).
_legacy_pw   = st.secrets.get("dashboard_password", "")
_clients_cfg = st.secrets.get("clients", {})

_client = None
if _legacy_pw or _clients_cfg:
    _entered = st.text_input("Password", type="password", key="_auth_pw")
    _ok, _client = authenticate(_entered, _legacy_pw, _clients_cfg)
    if not _ok:
        if _entered:
            st.error("Incorrect password.")
        st.stop()

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
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
section[data-testid="stSidebar"] h2 { color: #7c3aed; }
.badge-high    { color: #fc8181; font-weight: 600; }
.badge-medium  { color: #f6ad55; font-weight: 600; }
.badge-low     { color: #68d391; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Excel export helper ───────────────────────────────────────────────────────

def build_excel(vertical, period_label, primary_df, secondaries, exceptions_df, stats, entity_summary):
    """Build a multi-sheet Excel workbook and return bytes."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:

        # Sheet 1 — Summary
        summary_rows = [
            ["AgriSolve SME — Reconciliation Report"],
            [f"Vertical: {vertical.name}"],
            [f"Period: {period_label}"],
            [],
            ["KPI", "Value"],
            [stats["kpi1_label"], stats["kpi1_value"]],
            [stats["kpi2_label"], stats["kpi2_value"]],
            [stats["kpi3_label"], stats["kpi3_value"]],
            [stats["kpi4_label"], stats["kpi4_value"]],
            [stats["kpi5_label"], stats["kpi5_value"]],
            [stats["kpi6_label"], stats["kpi6_value"]],
            [],
            [f"Expected vs Received by {vertical.counterparty_label}"],
        ]
        df_summary = pd.DataFrame(summary_rows)
        df_summary.to_excel(writer, sheet_name="Summary", index=False, header=False)

        # Append entity summary below
        df_entity = pd.DataFrame(entity_summary)
        df_entity.to_excel(writer, sheet_name="Summary", index=False, startrow=len(summary_rows) + 1)

        # Sheet 2 — Exception Report
        if not exceptions_df.empty:
            exceptions_df.to_excel(writer, sheet_name="Exception Report", index=False)
        else:
            pd.DataFrame([["No exceptions found"]]).to_excel(
                writer, sheet_name="Exception Report", index=False, header=False
            )

        # Sheet 3 — Dispute Queue
        if not exceptions_df.empty:
            queue = exceptions_df[["counterparty", "entity_id", "description",
                                   "exception_type", "variance", "severity"]].copy()
            queue["dispute_status"] = "To Dispute"
            queue["variance_abs"]   = queue["variance"].abs().round(2)
            queue.to_excel(writer, sheet_name="Dispute Queue", index=False)

        # Sheet 4 — Primary data
        primary_df.to_excel(writer, sheet_name="Source Data", index=False)

    buf.seek(0)
    return buf.read()


# ── Email digest helper ───────────────────────────────────────────────────────

def send_email_digest(to_email: str, vertical_name: str, period_label: str,
                      stats: dict, exceptions_df: pd.DataFrame, excel_bytes: bytes) -> str:
    """Send exception summary email with Excel attached. Returns '' on success, error string on failure."""
    try:
        secrets = st.secrets.get("smtp", {})
        host    = secrets.get("host", "smtp.gmail.com")
        port    = int(secrets.get("port", 587))
        user    = secrets.get("user", "")
        pwd     = secrets.get("password", "")
        from_   = secrets.get("from", user)

        if not user or not pwd:
            return "SMTP credentials not configured. Add [smtp] section to .streamlit/secrets.toml"

        n_exc = len(exceptions_df)
        at_risk = exceptions_df["variance"].abs().sum() if not exceptions_df.empty else 0

        html = f"""
<html><body style="font-family:Arial,sans-serif;color:#222;max-width:600px">
<h2 style="color:#7c3aed">AgriSolve SME — {vertical_name} Digest</h2>
<p><strong>Period:</strong> {period_label}</p>
<hr>
<h3>KPI Summary</h3>
<table style="border-collapse:collapse;width:100%">
  <tr style="background:#f3f4f6"><th style="padding:8px;text-align:left">KPI</th><th style="padding:8px;text-align:right">Value</th></tr>
  <tr><td style="padding:8px">{stats['kpi1_label']}</td><td style="padding:8px;text-align:right"><strong>{stats['kpi1_value']}</strong></td></tr>
  <tr style="background:#f3f4f6"><td style="padding:8px">{stats['kpi2_label']}</td><td style="padding:8px;text-align:right"><strong>{stats['kpi2_value']}</strong></td></tr>
  <tr><td style="padding:8px">{stats['kpi3_label']}</td><td style="padding:8px;text-align:right"><strong>{stats['kpi3_value']}</strong></td></tr>
  <tr style="background:#f3f4f6"><td style="padding:8px">{stats['kpi4_label']}</td><td style="padding:8px;text-align:right"><strong>{stats['kpi4_value']}</strong></td></tr>
  <tr><td style="padding:8px">{stats['kpi5_label']}</td><td style="padding:8px;text-align:right"><strong>{stats['kpi5_value']}</strong></td></tr>
  <tr style="background:#f3f4f6"><td style="padding:8px">{stats['kpi6_label']}</td><td style="padding:8px;text-align:right"><strong>{stats['kpi6_value']}</strong></td></tr>
</table>
<h3 style="color:{'#e53e3e' if n_exc > 0 else '#38a169'}">
  {n_exc} Exception(s) Found — R {at_risk:,.2f} at risk
</h3>
{'<p>See attached Excel workbook for full exception list and dispute queue.</p>' if n_exc > 0 else '<p>✅ All records reconcile within tolerance.</p>'}
<hr>
<p style="font-size:12px;color:#666">AgriSolve (Pty) Ltd · SME Analytics Platform · R5,000 setup + R1,500/month</p>
</body></html>"""

        msg = MIMEMultipart("mixed")
        msg["From"]    = from_
        msg["To"]      = to_email
        msg["Subject"] = f"[AgriSolve SME] {vertical_name} — {period_label} Reconciliation Digest"
        msg.attach(MIMEText(html, "html"))

        # Attach Excel
        att = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        att.set_payload(excel_bytes)
        encoders.encode_base64(att)
        att.add_header("Content-Disposition", f'attachment; filename="AgriSolve_{vertical_name}_{period_label}.xlsx"')
        msg.attach(att)

        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls()
            server.login(user, pwd)
            server.sendmail(from_, to_email, msg.as_string())

        return ""
    except Exception as e:
        return str(e)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## AgriSolve SME")
    st.markdown("---")

    if _client:
        st.caption(f"Signed in as **{_client.get('display_name', _client['client_id'])}**")
    _visible_verticals = allowed_verticals(_client, list(REGISTRY.keys()))
    if not _visible_verticals:
        st.error("Your account isn't configured for any vertical. Contact AgriSolve support.")
        st.stop()
    vertical_name = st.selectbox("Business vertical", _visible_verticals)
    vertical = REGISTRY[vertical_name]()

    st.markdown("---")

    # Period selector
    st.markdown("**Reporting Period**")
    today = date.today()
    col_m, col_y = st.columns(2)
    month_names = list(calendar.month_abbr)[1:]
    sel_month = col_m.selectbox("Month", month_names, index=today.month - 2 if today.month > 1 else 0)
    sel_year  = col_y.selectbox("Year", list(range(2024, today.year + 1)), index=today.year - 2024)
    period_month = month_names.index(sel_month) + 1
    period_label = f"{sel_month} {sel_year}"

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
            try:
                primary_df = pd.read_csv(reg_file)
            except Exception as e:
                st.error(f"Could not read '{reg_file.name}': {e}")
                primary_df = None

        st.markdown(f"**{labels['secondary_label']}**")
        stmt_files = st.file_uploader(
            labels["secondary_caption"], type="csv",
            accept_multiple_files=True, key="stmt",
        )
        key_col = labels["secondary_key_column"]
        for f in stmt_files:
            try:
                df = pd.read_csv(f)
            except Exception as e:
                st.error(f"Could not read '{f.name}': {e}")
                continue
            if key_col in df.columns and not df.empty:
                secondaries[df[key_col].iloc[0]] = df

    st.markdown("---")

    # Email digest
    st.markdown("**📧 Email Digest**")
    digest_email = st.text_input("Send report to:", placeholder="client@example.com")
    send_digest  = st.button("Send Digest", use_container_width=True)

    st.markdown("---")
    st.caption(f"AgriSolve SME · {vertical.name} v1.1")


# ── Guard: require data ───────────────────────────────────────────────────────
if primary_df is None or not secondaries:
    st.info("Select a vertical and data source to begin.")
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


# ── Excel export (build once, used in header + digest) ───────────────────────
excel_bytes = build_excel(vertical, period_label, primary_df, secondaries,
                          exceptions_df, stats, entity_summary)


# ── Email digest trigger ──────────────────────────────────────────────────────
if send_digest:
    if not digest_email or "@" not in digest_email:
        st.sidebar.error("Enter a valid email address.")
    else:
        with st.spinner("Sending digest..."):
            err = send_email_digest(digest_email, vertical.name, period_label,
                                    stats, exceptions_df, excel_bytes)
        if err:
            st.sidebar.error(f"Send failed: {err}")
        else:
            st.sidebar.success(f"✅ Digest sent to {digest_email}")


# ── Page header with period + exports ────────────────────────────────────────
hc1, hc2, hc3 = st.columns([4, 1, 1])
hc1.markdown(f"### {vertical.name} · {period_label}")
hc2.download_button(
    "⬇️ CSV",
    data=exceptions_df.to_csv(index=False).encode("utf-8") if not exceptions_df.empty else b"No exceptions",
    file_name=f"exceptions_{vertical_name.replace(' ', '_')}_{period_label.replace(' ', '_')}.csv",
    mime="text/csv",
    use_container_width=True,
)
hc3.download_button(
    "📊 Excel",
    data=excel_bytes,
    file_name=f"AgriSolve_{vertical_name.replace(' ', '_')}_{period_label.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)


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
    st.subheader(f"{period_label} — {vertical.name} Summary")

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
    if "expected" in extra_cols: fmt["Expected (R)"] = "R {:,.2f}"
    if "actual"   in extra_cols: fmt["Received (R)"] = "R {:,.2f}"

    styled = (
        filtered[display_cols]
        .rename(columns=col_labels)
        .style
        .map(colour_severity, subset=["Severity"])
        .format(fmt)
    )
    st.dataframe(styled, use_container_width=True, height=500)

    dc1, dc2 = st.columns(2)
    dc1.download_button(
        "⬇️ Download exceptions CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name=f"exceptions_{period_label.replace(' ', '_')}.csv",
        mime="text/csv",
    )
    dc2.download_button(
        "📊 Download Excel workbook",
        data=excel_bytes,
        file_name=f"AgriSolve_{vertical_name.replace(' ', '_')}_{period_label.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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

        rc1, rc2 = st.columns(2)
        rc1.download_button(
            "Export dispute queue CSV",
            data=queue_display.to_csv(index=False).encode("utf-8"),
            file_name=f"dispute_queue_{period_label.replace(' ', '_')}.csv",
            mime="text/csv",
        )
        rc2.download_button(
            "📊 Full Excel workbook",
            data=excel_bytes,
            file_name=f"AgriSolve_{vertical_name.replace(' ', '_')}_{period_label.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.info(
            f"Raise these {len(queue)} disputes with your {rt['counterparty_noun']} "
            f"this week. At a 60% recovery rate, expect "
            f"**R {total_queue * 0.6:,.0f}** back next month."
        )
