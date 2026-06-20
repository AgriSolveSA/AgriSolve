"""
VerticalBase — Abstract base class for all AgriSolve SME verticals.

Every vertical must implement all abstract members. app.py calls only
these — no vertical-specific code ever leaks into the UI layer.

Data flow (one-directional, each layer independently testable):
    demo_data / upload
          ↓
    schema.py        (validate_inputs)
          ↓
    reconcile_logic  (run_reconciliation)
          ↓
    kpis.py          (get_summary_stats / get_entity_summary)
          ↓
    app.py           (render only — imports verticals via REGISTRY)
"""

import abc
import calendar
import datetime
import pandas as pd

_MONTH_NAMES = list(calendar.month_name)  # index 0 is '', 1='January', ... 12='December'


def month_period_labels(period_month: int | None = None, period_year: int | None = None) -> tuple[str, str]:
    """
    Returns (prior_month_label, current_month_label), e.g. ('February 2026', 'March 2026'),
    for verticals whose Recovery Tracker reports monthly. Handles the January ->
    December-of-prior-year rollover. Defaults to the real current month/year so
    call sites (and tests) that don't pass a period still get a sensible label
    instead of a crash.
    """
    today = datetime.date.today()
    month = period_month or today.month
    year  = period_year or today.year
    prior_month = month - 1 or 12
    prior_year  = year - 1 if month == 1 else year
    return f"{_MONTH_NAMES[prior_month]} {prior_year}", f"{_MONTH_NAMES[month]} {year}"


def quarter_period_labels(period_month: int | None = None, period_year: int | None = None) -> tuple[str, str]:
    """
    Returns (prior_quarter_label, current_quarter_label), e.g. ('Q3 2025', 'Q4 2025'),
    for verticals whose Recovery Tracker reports quarterly. Handles the Q1 ->
    Q4-of-prior-year rollover.
    """
    today = datetime.date.today()
    month = period_month or today.month
    year  = period_year or today.year
    quarter = (month - 1) // 3 + 1
    prior_quarter = quarter - 1 or 4
    prior_year    = year - 1 if quarter == 1 else year
    return f"Q{prior_quarter} {prior_year}", f"Q{quarter} {year}"


class VerticalBase(abc.ABC):
    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Display name, e.g. 'Insurance Broker'."""

    @property
    @abc.abstractmethod
    def icon(self) -> str:
        """Single emoji icon, e.g. '🏦'."""

    @property
    @abc.abstractmethod
    def primary_entity_label(self) -> str:
        """Noun for the primary record: 'Policy', 'Invoice', 'Project', 'Trip'."""

    @property
    @abc.abstractmethod
    def counterparty_label(self) -> str:
        """Noun for the counterparty: 'Insurer', 'Client', 'Contractor', 'Vehicle'."""

    # ── Data ──────────────────────────────────────────────────────────────────

    @abc.abstractmethod
    def generate_demo(self) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
        """
        Return (primary_df, {counterparty_name: secondary_df}).
        Used by app.py when the user selects 'Demo data'.
        """

    @abc.abstractmethod
    def validate_inputs(
        self,
        primary_df: pd.DataFrame,
        secondaries: dict[str, pd.DataFrame],
    ) -> list[str]:
        """
        Validate the primary and secondary DataFrames.
        Returns a list of human-readable error strings; empty list means valid.
        """

    # ── Reconciliation ────────────────────────────────────────────────────────

    @abc.abstractmethod
    def run_reconciliation(
        self,
        primary_df: pd.DataFrame,
        secondaries: dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        """
        Detect and return exception rows only.

        Output DataFrame MUST contain these standard columns so app.py
        can render them without vertical-specific knowledge:
            entity_id      — primary record identifier
            counterparty   — which counterparty the exception is against
            description    — human-readable subject (client name, etc.)
            exception_type — string code, e.g. 'RATE_MISMATCH'
            severity       — 'High' | 'Medium' | 'Low'
            variance       — signed numeric amount (negative = shortfall)

        Additional columns are allowed and will be shown in the table.
        """

    # ── Summaries ─────────────────────────────────────────────────────────────

    @abc.abstractmethod
    def get_summary_stats(
        self,
        primary_df: pd.DataFrame,
        secondaries: dict[str, pd.DataFrame],
        exceptions_df: pd.DataFrame,
    ) -> dict:
        """
        Return KPI values for the 6-card header row.

        Required keys:
            kpi1_label, kpi1_value
            kpi2_label, kpi2_value
            kpi3_label, kpi3_value, kpi3_delta, kpi3_positive (bool)
            kpi4_label, kpi4_value
            kpi5_label, kpi5_value
            kpi6_label, kpi6_value

        Values should be pre-formatted strings ready for st.metric().
        """

    @abc.abstractmethod
    def get_entity_summary(
        self,
        primary_df: pd.DataFrame,
        secondaries: dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        """
        Per-counterparty roll-up for the grouped bar chart.

        Required columns: entity, expected, actual
        Optional columns: variance
        """

    # ── UI labels ─────────────────────────────────────────────────────────────

    @abc.abstractmethod
    def get_recovery_tracker_label(self, period_month: int | None = None, period_year: int | None = None) -> dict:
        """
        Return all strings and static data for the Recovery Tracker page.

        period_month/period_year (1-12, e.g. 2026) come from app.py's sidebar
        period selector and must drive prior_section/current_section -- these
        used to be hardcoded fixed dates in every vertical, so switching the
        period dropdown never actually changed what the Recovery Tracker
        claimed the period was. Defaults to the real current date so existing
        callers that don't pass a period still get a sensible label.

        Required keys:
            prior_section     — e.g. 'Prior Month — February 2026' (use
                                 month_period_labels()/quarter_period_labels()
                                 from this module, not a hardcoded string)
            current_section   — e.g. 'Current Month — March 2026 (New Exceptions)'
            disputed_label, disputed_value
            recovered_label, recovered_value, recovered_delta
            pending_label, pending_value
            prior_rows        — list[dict] for the prior-month summary table
            entity_noun       — e.g. 'exceptions', 'invoices'
            counterparty_noun — e.g. 'insurers', 'clients'
        """

    @abc.abstractmethod
    def get_upload_labels(self) -> dict:
        """
        Return sidebar upload widget labels.

        Required keys:
            primary_label         — section heading for the primary upload
            primary_caption       — file_uploader label
            secondary_label       — section heading for the secondary uploads
            secondary_caption     — file_uploader label
            demo_caption          — caption shown in Demo data mode
            secondary_key_column  — column used as the dict key for secondaries
        """
