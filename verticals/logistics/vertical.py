"""
Logistics vertical.
Single job: implement VerticalBase by delegating to demo_data, schema,
reconcile_logic, and kpis. No business logic lives here.
"""

import pandas as pd
from verticals.base import VerticalBase, month_period_labels
from verticals.logistics import demo_data, schema, reconcile_logic, kpis


class LogisticsVertical(VerticalBase):
    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return "Logistics"

    @property
    def icon(self) -> str:
        return "🚛"

    @property
    def primary_entity_label(self) -> str:
        return "Trip"

    @property
    def counterparty_label(self) -> str:
        return "Vehicle"

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

    def get_recovery_tracker_label(self, period_month: int | None = None, period_year: int | None = None) -> dict:
        prior_label, current_label = month_period_labels(period_month, period_year)
        return {
            "prior_section":   f"Prior Month — {prior_label}",
            "current_section": f"Current Month — {current_label} (New Exceptions)",

            "disputed_label":  "Loss-Making Trips",
            "disputed_value":  "R 18,450",

            "recovered_label": "Recovered (Rerouted)",
            "recovered_value": "R 12,300",
            "recovered_delta": "67% recovery rate",

            "pending_label": "Under Review",
            "pending_value": "R 6,150",

            "prior_rows": [
                {
                    "Trip #":   "TR-0022",
                    "Vehicle":  "VEH-003",
                    "Loss":     "R 7,200",
                    "Status":   "Recovered",
                    "Recovered":"R 7,200",
                    "Notes":    "Rerouted via N1 — fuel saving achieved",
                },
                {
                    "Trip #":   "TR-0047",
                    "Vehicle":  "VEH-001",
                    "Loss":     "R 3,100",
                    "Status":   "Recovered",
                    "Recovered":"R 2,000",
                    "Notes":    "Partial — driver coaching applied",
                },
                {
                    "Trip #":   "TR-0063",
                    "Vehicle":  "VEH-004",
                    "Loss":     "R 8,150",
                    "Status":   "In Review",
                    "Recovered":"—",
                    "Notes":    "High fuel anomaly under investigation",
                },
            ],

            "entity_noun":       "trips",
            "counterparty_noun": "vehicles",
        }

    def get_upload_labels(self) -> dict:
        return {
            "primary_label":        "Trip Manifest",
            "primary_caption":      "Upload manifest CSV",
            "secondary_label":      "Fleet Cost Sheet",
            "secondary_caption":    "Upload one CSV per fleet (monthly fixed costs)",
            "demo_caption":         "March 2026 · 4 vehicles · 6 loss-making trips seeded",
            "secondary_key_column": "vehicle_id",
        }
