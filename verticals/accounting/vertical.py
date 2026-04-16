"""
Accounting Firm vertical.
Single job: implement VerticalBase by delegating to demo_data, schema,
reconcile_logic, and kpis.  No business logic lives here.
"""

import pandas as pd
from verticals.base import VerticalBase
from verticals.accounting import demo_data, schema, reconcile_logic, kpis


class AccountingVertical(VerticalBase):
    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return "Accounting Firm"

    @property
    def icon(self) -> str:
        return "📊"

    @property
    def primary_entity_label(self) -> str:
        return "Invoice"

    @property
    def counterparty_label(self) -> str:
        return "Client"

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
            "disputed_value":  "R 18,200",

            "recovered_label": "Recovered",
            "recovered_value": "R 12,400",
            "recovered_delta": "68% recovery rate",

            "pending_label":   "Pending",
            "pending_value":   "R 5,800",

            "prior_rows": [
                {
                    "Invoice #": "INV-NFC-005",
                    "Client":    "Ndlovu Farming Co",
                    "Disputed":  "R 8,500",
                    "Status":    "Recovered",
                    "Recovered": "R 8,500",
                    "Notes":     "Payment received after follow-up",
                },
                {
                    "Invoice #": "INV-CHL-009",
                    "Client":    "Cape Harvest Ltd",
                    "Disputed":  "R 3,900",
                    "Status":    "Recovered",
                    "Recovered": "R 3,900",
                    "Notes":     "Billing query resolved",
                },
                {
                    "Invoice #": "INV-BAS-004",
                    "Client":    "Boland Agri Solutions",
                    "Disputed":  "R 5,800",
                    "Status":    "In Dispute",
                    "Recovered": "—",
                    "Notes":     "Awaiting client response",
                },
            ],

            "entity_noun":       "invoices",
            "counterparty_noun": "clients",
        }

    def get_upload_labels(self) -> dict:
        return {
            "primary_label":        "AR Register",
            "primary_caption":      "Upload AR register CSV",
            "secondary_label":      "Client Remittances",
            "secondary_caption":    "Upload one remittance CSV per client",
            "demo_caption":         "45 invoices · 3 clients · 7 seeded exceptions",
            "secondary_key_column": "client_name",
        }
