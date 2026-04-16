"""
Insurance Broker vertical tests — demo_data, reconcile_logic, kpis, schema.

Each class tests exactly one module in isolation.
No Streamlit, no mocks, no cross-module dependencies.
"""

import pandas as pd
import pytest

from verticals.insurance_broker.demo_data import generate_demo
from verticals.insurance_broker.reconcile_logic import run_reconciliation
from verticals.insurance_broker.kpis import get_summary_stats, get_entity_summary
from verticals.insurance_broker.schema import (
    validate_all,
    validate_register,
    validate_statement,
)


# ── demo_data ─────────────────────────────────────────────────────────────────

class TestDemoData:

    def test_register_has_240_rows(self):
        reg, _ = generate_demo()
        assert len(reg) == 240

    def test_three_insurers_in_statements(self):
        _, stmts = generate_demo()
        assert len(stmts) == 3

    def test_register_required_columns_present(self):
        reg, _ = generate_demo()
        required = {
            "policy_number", "insurer_name", "policy_status",
            "agreed_commission_rate", "monthly_premium",
            "expected_monthly_commission",
        }
        assert required <= set(reg.columns)

    def test_each_statement_has_required_columns(self):
        _, stmts = generate_demo()
        required = {
            "policy_number", "insurer_name",
            "commission_amount", "commission_rate", "monthly_premium",
        }
        for insurer, df in stmts.items():
            missing = required - set(df.columns)
            assert not missing, f"Statement '{insurer}' missing columns: {missing}"

    def test_register_active_policies_have_positive_expected_commission(self):
        reg, _ = generate_demo()
        active = reg[reg["policy_status"] == "Active"]
        assert (active["expected_monthly_commission"] >= 0).all()


# ── reconcile_logic ───────────────────────────────────────────────────────────

class TestReconcileLogic:

    def test_returns_exactly_8_seeded_exceptions(self):
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        assert len(exc) == 8

    def test_standard_columns_all_present(self):
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        for col in ("entity_id", "counterparty", "description",
                    "exception_type", "severity", "variance"):
            assert col in exc.columns, f"Missing standard column: {col}"

    def test_all_four_exception_types_present(self):
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        types = set(exc["exception_type"])
        assert "MISSING_COMMISSION" in types
        assert "INVALID_POLICY_PAID" in types
        assert "RATE_MISMATCH" in types
        assert "GHOST_POLICY" in types

    def test_severity_values_within_allowed_set(self):
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        assert set(exc["severity"]).issubset({"High", "Medium", "Low"})

    def test_sorted_high_exceptions_first(self):
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        sev_order = {"High": 0, "Medium": 1, "Low": 2}
        ranks = exc["severity"].map(sev_order).tolist()
        assert ranks == sorted(ranks)

    def test_empty_secondaries_returns_empty_dataframe(self):
        reg, _ = generate_demo()
        exc = run_reconciliation(reg, {})
        assert isinstance(exc, pd.DataFrame)
        assert exc.empty


# ── kpis ──────────────────────────────────────────────────────────────────────

class TestKpis:

    def test_all_required_stat_keys_returned(self):
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        stats = get_summary_stats(reg, stmts, exc)
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

    def test_exception_count_is_8(self):
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        stats = get_summary_stats(reg, stmts, exc)
        assert stats["kpi4_value"] == "8"

    def test_total_at_risk_matches_seeded_amount(self):
        """Seeded discrepancies total R10,579.25 → formatted as 'R 10,579'."""
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        stats = get_summary_stats(reg, stmts, exc)
        assert stats["kpi6_value"] == "R 10,579"

    def test_kpi3_positive_is_bool(self):
        reg, stmts = generate_demo()
        exc = run_reconciliation(reg, stmts)
        stats = get_summary_stats(reg, stmts, exc)
        assert isinstance(stats["kpi3_positive"], bool)

    def test_entity_summary_has_required_columns(self):
        reg, stmts = generate_demo()
        es = get_entity_summary(reg, stmts)
        assert {"entity", "expected", "actual"} <= set(es.columns)

    def test_entity_summary_has_one_row_per_insurer(self):
        reg, stmts = generate_demo()
        es = get_entity_summary(reg, stmts)
        assert len(es) == 3

    def test_entity_summary_expected_values_positive(self):
        reg, stmts = generate_demo()
        es = get_entity_summary(reg, stmts)
        assert (es["expected"] >= 0).all()


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema:

    def test_full_demo_data_passes_validation(self):
        reg, stmts = generate_demo()
        assert validate_all(reg, stmts) == []

    def test_valid_minimal_register_passes(self, ib_register):
        assert validate_register(ib_register) == []

    def test_valid_minimal_statement_passes(self, ib_statement):
        assert validate_statement("Test Insurer", ib_statement) == []

    def test_register_missing_policy_status_returns_error(self, ib_register):
        bad = ib_register.drop(columns=["policy_status"])
        errors = validate_register(bad)
        assert len(errors) > 0
        assert any("policy_status" in e for e in errors)

    def test_statement_missing_commission_amount_returns_error(self, ib_statement):
        bad = ib_statement.drop(columns=["commission_amount"])
        errors = validate_statement("Test Insurer", bad)
        assert len(errors) > 0
        assert any("commission_amount" in e for e in errors)

    def test_register_invalid_policy_status_returns_error(self, ib_register):
        bad = ib_register.copy()
        bad.loc[0, "policy_status"] = "INVALID_STATUS"
        errors = validate_register(bad)
        assert len(errors) > 0

    def test_register_negative_premium_returns_error(self, ib_register):
        bad = ib_register.copy()
        bad.loc[0, "monthly_premium"] = -100
        errors = validate_register(bad)
        assert len(errors) > 0

    def test_validate_all_reports_errors_from_all_sources(self, ib_register, ib_statement):
        bad_reg  = ib_register.drop(columns=["policy_status"])
        bad_stmt = ib_statement.drop(columns=["commission_amount"])
        errors = validate_all(bad_reg, {"Test": bad_stmt})
        # Errors from both register and statement
        assert len(errors) >= 2
