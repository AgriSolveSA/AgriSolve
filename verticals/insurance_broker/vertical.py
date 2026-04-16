"""
Insurance Broker vertical.
Single job: implement VerticalBase by delegating to the module-level
functions in demo_data, schema, reconcile_logic, and kpis.

No business logic lives here — this file is a wiring layer only.
"""

import pandas as pd
from verticals.base import VerticalBase
from verticals.insurance_broker import demo_data, schema, reconcile_logic, kpis


class InsuranceBrokerVertical(VerticalBase):
    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return "Insurance Broker"

    @property
    def icon(self) -> str:
        return "🏦"

    @property
    def primary_entity_label(self) -> str:
        return "Policy"

    @property
    def counterparty_label(self) -> str:
        return "Insurer"

    # ── Data ──────────────────────────────────────────────────────────────────

    def generate_demo(self) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
        return demo_data.generate_demo()

    def validate_inputs(
        self,
        primary_df: pd.DataFrame,
        secondaries: dict[str, pd.DataFrame],
    ) -> list[str]:
        return schema.validate_all(primary_df, secondaries)

    # ── Reconciliation ────────────────────────────────────────────────────────

    def run_reconciliation(
        self,
        primary_df: pd.DataFrame,
        secondaries: dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        return reconcile_logic.run_reconciliation(primary_df, secondaries)

    # ── Summaries ─────────────────────────────────────────────────────────────

    def get_summary_stats(
        self,
        primary_df: pd.DataFrame,
        secondaries: dict[str, pd.DataFrame],
        exceptions_df: pd.DataFrame,
    ) -> dict:
        return kpis.get_summary_stats(primary_df, secondaries, exceptions_df)

    def get_entity_summary(
        self,
        primary_df: pd.DataFrame,
        secondaries: dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        return kpis.get_entity_summary(primary_df, secondaries)

    # ── UI labels ─────────────────────────────────────────────────────────────

    def get_recovery_tracker_label(self) -> dict:
        return {
            "prior_section":   "Prior Month — February 2026",
            "current_section": "Current Month — March 2026 (New Exceptions)",

            "disputed_label":  "Disputed",
            "disputed_value":  "R 9,250",

            "recovered_label": "Recovered",
            "recovered_value": "R 6,150",
            "recovered_delta": "66% recovery rate",

            "pending_label":   "Pending",
            "pending_value":   "R 3,100",

            "prior_rows": [
                {
                    "Policy #": "POL-1102",
                    "Insurer":  "Pinnacle Life Insurance",
                    "Disputed": "R 4,200",
                    "Status":   "Recovered",
                    "Recovered":"R 4,200",
                    "Notes":    "Insurer confirmed error",
                },
                {
                    "Policy #": "POL-2045",
                    "Insurer":  "Meridian Short-Term",
                    "Disputed": "R 1,950",
                    "Status":   "Recovered",
                    "Recovered":"R 1,950",
                    "Notes":    "Rate correction applied",
                },
                {
                    "Policy #": "POL-3019",
                    "Insurer":  "Apex Financial Services",
                    "Disputed": "R 3,100",
                    "Status":   "In Dispute",
                    "Recovered":"—",
                    "Notes":    "Awaiting insurer response",
                },
            ],

            "entity_noun":       "exceptions",
            "counterparty_noun": "insurers",
        }

    def get_upload_labels(self) -> dict:
        return {
            "primary_label":        "Policy Register",
            "primary_caption":      "Upload register CSV",
            "secondary_label":      "Commission Statements",
            "secondary_caption":    "Upload one CSV per insurer",
            "demo_caption":         "240 policies · 3 insurers · 8 seeded discrepancies",
            "secondary_key_column": "insurer_name",
        }
