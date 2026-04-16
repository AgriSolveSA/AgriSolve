"""
Accounting Firm vertical tests — demo_data, reconcile_logic, kpis, schema.

Each class tests exactly one module in isolation.
No Streamlit, no mocks, no cross-module dependencies.
"""

import pandas as pd
import pytest

from verticals.accounting.demo_data     import generate_demo
from verticals.accounting.reconcile_logic import run_reconciliation
from verticals.accounting.kpis          import get_summary_stats, get_entity_summary
from verticals.accounting.schema        import (
    validate_all,
    validate_register,
    validate_remittance,
)


# ── demo_data ─────────────────────────────────────────────────────────────────

class TestDemoData:

    def test_ar_register_has_45_rows(self):
        ar, _ = generate_demo()
        assert len(ar) == 45

    def test_three_clients_in_remittances(self):
        _, rems = generate_demo()
        assert len(rems) == 3

    def test_ar_register_required_columns_present(self):
        ar, _ = generate_demo()
        required = {
            "invoice_number", "client_name", "service_type",
            "invoice_date", "due_date", "contracted_amount",
            "invoice_amount", "paid_amount", "days_outstanding", "payment_status",
        }
        assert required <= set(ar.columns)

    def test_each_remittance_has_required_columns(self):
        _, rems = generate_demo()
        required = {
            "client_name", "invoice_reference",
            "payment_date", "amount_paid", "payment_method",
        }
        for client, df in rems.items():
            missing = required - set(df.columns)
            assert not missing, f"Remittance '{client}' missing columns: {missing}"

    def test_paid_invoices_have_non_negative_paid_amount(self):
        ar, _ = generate_demo()
        paid = ar[ar["payment_status"] == "Paid"]
        assert (paid["paid_amount"] >= 0).all()


# ── reconcile_logic ───────────────────────────────────────────────────────────

class TestReconcileLogic:

    def test_returns_exactly_7_seeded_exceptions(self):
        ar, rems = generate_demo()
        exc = run_reconciliation(ar, rems)
        assert len(exc) == 7

    def test_standard_columns_all_present(self):
        ar, rems = generate_demo()
        exc = run_reconciliation(ar, rems)
        for col in ("entity_id", "counterparty", "description",
                    "exception_type", "severity", "variance"):
            assert col in exc.columns, f"Missing standard column: {col}"

    def test_all_four_exception_types_present(self):
        ar, rems = generate_demo()
        exc = run_reconciliation(ar, rems)
        types = set(exc["exception_type"])
        assert "DEBTOR_OVERDUE" in types
        assert "EXPENSE_SPIKE"  in types
        assert "MARGIN_DROP"    in types
        assert "BANK_MISMATCH"  in types

    def test_severity_values_within_allowed_set(self):
        ar, rems = generate_demo()
        exc = run_reconciliation(ar, rems)
        assert set(exc["severity"]).issubset({"High", "Medium", "Low"})

    def test_sorted_high_exceptions_first(self):
        ar, rems = generate_demo()
        exc = run_reconciliation(ar, rems)
        sev_order = {"High": 0, "Medium": 1, "Low": 2}
        ranks = exc["severity"].map(sev_order).tolist()
        assert ranks == sorted(ranks)

    def test_empty_secondaries_returns_empty_dataframe(self):
        ar, _ = generate_demo()
        exc = run_reconciliation(ar, {})
        assert isinstance(exc, pd.DataFrame)
        assert exc.empty

    def test_debtor_overdue_has_three_exceptions(self):
        ar, rems = generate_demo()
        exc = run_reconciliation(ar, rems)
        assert (exc["exception_type"] == "DEBTOR_OVERDUE").sum() == 3


# ── kpis ──────────────────────────────────────────────────────────────────────

class TestKpis:

    def test_all_required_stat_keys_returned(self):
        ar, rems = generate_demo()
        exc   = run_reconciliation(ar, rems)
        stats = get_summary_stats(ar, rems, exc)
        required = {
            "kpi1_label", "kpi1_value",
            "kpi2_label", "kpi2_value",
            "kpi3_label", "kpi3_value", "kpi3_delta", "kpi3_positive",
            "kpi4_label", "kpi4_value",
            "kpi5_label", "kpi5_value",
            "kpi6_label", "kpi6_value",
        }
        missing = required - set(stats.keys())
        assert not missing, f"Missing stat keys: {missing}"

    def test_exception_count_is_7(self):
        ar, rems = generate_demo()
        exc   = run_reconciliation(ar, rems)
        stats = get_summary_stats(ar, rems, exc)
        assert stats["kpi4_value"] == "7"

    def test_high_priority_count_is_4(self):
        ar, rems = generate_demo()
        exc   = run_reconciliation(ar, rems)
        stats = get_summary_stats(ar, rems, exc)
        assert stats["kpi5_value"] == "4"

    def test_total_at_risk_matches_seeded_amount(self):
        """Seeded discrepancies total R33,050 → formatted as 'R 33,050'."""
        ar, rems = generate_demo()
        exc   = run_reconciliation(ar, rems)
        stats = get_summary_stats(ar, rems, exc)
        assert stats["kpi6_value"] == "R 33,050"

    def test_kpi3_positive_is_bool(self):
        ar, rems = generate_demo()
        exc   = run_reconciliation(ar, rems)
        stats = get_summary_stats(ar, rems, exc)
        assert isinstance(stats["kpi3_positive"], bool)

    def test_entity_summary_has_required_columns(self):
        ar, rems = generate_demo()
        es = get_entity_summary(ar, rems)
        assert {"entity", "expected", "actual"} <= set(es.columns)

    def test_entity_summary_has_one_row_per_client(self):
        ar, rems = generate_demo()
        es = get_entity_summary(ar, rems)
        assert len(es) == 3

    def test_entity_summary_expected_values_positive(self):
        ar, rems = generate_demo()
        es = get_entity_summary(ar, rems)
        assert (es["expected"] >= 0).all()


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema:

    def test_full_demo_data_passes_validation(self):
        ar, rems = generate_demo()
        assert validate_all(ar, rems) == []

    def test_valid_minimal_register_passes(self, acc_register):
        assert validate_register(acc_register) == []

    def test_valid_minimal_remittance_passes(self, acc_remittance):
        assert validate_remittance("Test Client", acc_remittance) == []

    def test_register_missing_payment_status_returns_error(self, acc_register):
        bad    = acc_register.drop(columns=["payment_status"])
        errors = validate_register(bad)
        assert len(errors) > 0
        assert any("payment_status" in e for e in errors)

    def test_remittance_missing_amount_paid_returns_error(self, acc_remittance):
        bad    = acc_remittance.drop(columns=["amount_paid"])
        errors = validate_remittance("Test Client", bad)
        assert len(errors) > 0
        assert any("amount_paid" in e for e in errors)

    def test_register_invalid_payment_status_returns_error(self, acc_register):
        bad = acc_register.copy()
        bad.loc[0, "payment_status"] = "UNKNOWN_STATUS"
        errors = validate_register(bad)
        assert len(errors) > 0

    def test_register_negative_invoice_amount_returns_error(self, acc_register):
        bad = acc_register.copy()
        bad.loc[0, "invoice_amount"] = -500.0
        errors = validate_register(bad)
        assert len(errors) > 0

    def test_validate_all_reports_errors_from_all_sources(self, acc_register, acc_remittance):
        bad_reg = acc_register.drop(columns=["payment_status"])
        bad_rem = acc_remittance.drop(columns=["amount_paid"])
        errors  = validate_all(bad_reg, {"Test Client": bad_rem})
        assert len(errors) >= 2
