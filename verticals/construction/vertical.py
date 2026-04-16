"""
Construction vertical.
Single job: implement VerticalBase by delegating to demo_data, schema,
reconcile_logic, and kpis.  No business logic lives here.
"""

import pandas as pd
from verticals.base import VerticalBase
from verticals.construction import demo_data, schema, reconcile_logic, kpis


class ConstructionVertical(VerticalBase):
    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return "Construction"

    @property
    def icon(self) -> str:
        return "🏗️"

    @property
    def primary_entity_label(self) -> str:
        return "Project"

    @property
    def counterparty_label(self) -> str:
        return "Contractor"

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
            "prior_section":   "Prior Quarter — Q3 2025",
            "current_section": "Current Quarter — Q4 2025 (New Exceptions)",

            "disputed_label":  "Disputed",
            "disputed_value":  "R 45,200",

            "recovered_label": "Recovered",
            "recovered_value": "R 28,700",
            "recovered_delta": "63% recovery rate",

            "pending_label":   "Pending",
            "pending_value":   "R 16,500",

            "prior_rows": [
                {
                    "Project #":   "PRJ-VW-001",
                    "Contractor":  "Veld & Weg Builders",
                    "Disputed":    "R 21,500",
                    "Status":      "Recovered",
                    "Recovered":   "R 21,500",
                    "Notes":       "Payment received after escalation",
                },
                {
                    "Project #":   "PRJ-NC-002",
                    "Contractor":  "Ndlovu Construction",
                    "Disputed":    "R 14,200",
                    "Status":      "Recovered",
                    "Recovered":   "R 7,200",
                    "Notes":       "Partial recovery, variation order raised",
                },
                {
                    "Project #":   "PRJ-BC-001",
                    "Contractor":  "Boplaas Civils",
                    "Disputed":    "R 9,500",
                    "Status":      "In Dispute",
                    "Recovered":   "—",
                    "Notes":       "Awaiting quantity surveyor sign-off",
                },
            ],

            "entity_noun":       "projects",
            "counterparty_noun": "contractors",
        }

    def get_upload_labels(self) -> dict:
        return {
            "primary_label":        "Projects Register",
            "primary_caption":      "Upload projects register CSV",
            "secondary_label":      "Contractor Cost Lines",
            "secondary_caption":    "Upload one cost lines CSV per contractor",
            "demo_caption":         "7 projects · 3 contractors · 6 seeded exceptions",
            "secondary_key_column": "contractor_name",
        }
