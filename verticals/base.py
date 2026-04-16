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
import pandas as pd


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
    def get_recovery_tracker_label(self) -> dict:
        """
        Return all strings and static data for the Recovery Tracker page.

        Required keys:
            prior_section     — e.g. 'Prior Month — February 2026'
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
