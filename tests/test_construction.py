"""
Construction vertical tests — demo_data, reconcile_logic, kpis, schema.

Each class tests exactly one module in isolation.
No Streamlit, no mocks, no cross-module dependencies.
"""

import pandas as pd
import pytest

from verticals.construction.demo_data      import generate_demo
from verticals.construction.reconcile_logic import run_reconciliation
from verticals.construction.kpis           import get_summary_stats, get_entity_summary
from verticals.construction.schema         import (
    validate_all,
    validate_projects,
    validate_cost_lines,
)


# ── demo_data ─────────────────────────────────────────────────────────────────

class TestDemoData:

    def test_projects_has_7_rows(self):
        projects, _ = generate_demo()
        assert len(projects) == 7

    def test_three_contractors_in_cost_lines(self):
        _, costs = generate_demo()
        assert len(costs) == 3

    def test_projects_required_columns_present(self):
        projects, _ = generate_demo()
        required = {
            "project_number", "project_name", "contractor_name",
            "start_date", "end_date", "contract_value",
            "budgeted_cost", "actual_cost", "billed_amount",
            "payment_received", "days_outstanding", "payment_status",
        }
        assert required <= set(projects.columns)

    def test_each_cost_lines_has_required_columns(self):
        _, costs = generate_demo()
        required = {
            "project_number", "contractor_name", "cost_category",
            "description", "budgeted_amount", "actual_amount", "invoice_date",
        }
        for contractor, df in costs.items():
            missing = required - set(df.columns)
            assert not missing, f"Cost lines '{contractor}' missing columns: {missing}"

    def test_paid_projects_have_non_negative_payment_received(self):
        projects, _ = generate_demo()
        paid = projects[projects["payment_status"] == "Paid"]
        assert (paid["payment_received"] >= 0).all()


# ── reconcile_logic ───────────────────────────────────────────────────────────

class TestReconcileLogic:

    def test_returns_exactly_6_seeded_exceptions(self):
        projects, costs = generate_demo()
        exc = run_reconciliation(projects, costs)
        assert len(exc) == 6

    def test_standard_columns_all_present(self):
        projects, costs = generate_demo()
        exc = run_reconciliation(projects, costs)
        for col in ("entity_id", "counterparty", "description",
                    "exception_type", "severity", "variance"):
            assert col in exc.columns, f"Missing standard column: {col}"

    def test_all_three_exception_types_present(self):
        projects, costs = generate_demo()
        exc = run_reconciliation(projects, costs)
        types = set(exc["exception_type"])
        assert "COST_OVERRUN"   in types
        assert "SLOW_PAYMENT"   in types
        assert "MARGIN_EROSION" in types

    def test_severity_values_within_allowed_set(self):
        projects, costs = generate_demo()
        exc = run_reconciliation(projects, costs)
        assert set(exc["severity"]).issubset({"High", "Medium", "Low"})

    def test_sorted_high_exceptions_first(self):
        projects, costs = generate_demo()
        exc = run_reconciliation(projects, costs)
        sev_order = {"High": 0, "Medium": 1, "Low": 2}
        ranks = exc["severity"].map(sev_order).tolist()
        assert ranks == sorted(ranks)

    def test_exceptions_found_without_cost_lines(self):
        """All exceptions derive from the projects register — cost lines are not required."""
        projects, _ = generate_demo()
        exc = run_reconciliation(projects, {})
        assert len(exc) == 6

    def test_cost_overrun_has_two_exceptions(self):
        projects, costs = generate_demo()
        exc = run_reconciliation(projects, costs)
        assert (exc["exception_type"] == "COST_OVERRUN").sum() == 2


# ── kpis ──────────────────────────────────────────────────────────────────────

class TestKpis:

    def test_all_required_stat_keys_returned(self):
        projects, costs = generate_demo()
        exc   = run_reconciliation(projects, costs)
        stats = get_summary_stats(projects, costs, exc)
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

    def test_exception_count_is_6(self):
        projects, costs = generate_demo()
        exc   = run_reconciliation(projects, costs)
        stats = get_summary_stats(projects, costs, exc)
        assert stats["kpi4_value"] == "6"

    def test_high_priority_count_is_4(self):
        projects, costs = generate_demo()
        exc   = run_reconciliation(projects, costs)
        stats = get_summary_stats(projects, costs, exc)
        assert stats["kpi5_value"] == "4"

    def test_total_at_risk_matches_seeded_amount(self):
        """Seeded discrepancies total R428,000 → formatted as 'R 428,000'."""
        projects, costs = generate_demo()
        exc   = run_reconciliation(projects, costs)
        stats = get_summary_stats(projects, costs, exc)
        assert stats["kpi6_value"] == "R 428,000"

    def test_kpi3_positive_is_bool(self):
        projects, costs = generate_demo()
        exc   = run_reconciliation(projects, costs)
        stats = get_summary_stats(projects, costs, exc)
        assert isinstance(stats["kpi3_positive"], bool)

    def test_entity_summary_has_required_columns(self):
        projects, costs = generate_demo()
        es = get_entity_summary(projects, costs)
        assert {"entity", "expected", "actual"} <= set(es.columns)

    def test_entity_summary_has_one_row_per_contractor(self):
        projects, costs = generate_demo()
        es = get_entity_summary(projects, costs)
        assert len(es) == 3

    def test_entity_summary_expected_values_positive(self):
        projects, costs = generate_demo()
        es = get_entity_summary(projects, costs)
        assert (es["expected"] >= 0).all()


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema:

    def test_full_demo_data_passes_validation(self):
        projects, costs = generate_demo()
        assert validate_all(projects, costs) == []

    def test_valid_minimal_projects_passes(self, con_projects):
        assert validate_projects(con_projects) == []

    def test_valid_minimal_cost_lines_passes(self, con_cost_lines):
        assert validate_cost_lines("Test Contractor", con_cost_lines) == []

    def test_projects_missing_payment_status_returns_error(self, con_projects):
        bad    = con_projects.drop(columns=["payment_status"])
        errors = validate_projects(bad)
        assert len(errors) > 0
        assert any("payment_status" in e for e in errors)

    def test_cost_lines_missing_actual_amount_returns_error(self, con_cost_lines):
        bad    = con_cost_lines.drop(columns=["actual_amount"])
        errors = validate_cost_lines("Test Contractor", bad)
        assert len(errors) > 0
        assert any("actual_amount" in e for e in errors)

    def test_projects_invalid_payment_status_returns_error(self, con_projects):
        bad = con_projects.copy()
        bad.loc[0, "payment_status"] = "UNKNOWN_STATUS"
        errors = validate_projects(bad)
        assert len(errors) > 0

    def test_projects_negative_contract_value_returns_error(self, con_projects):
        bad = con_projects.copy()
        bad.loc[0, "contract_value"] = -500.0
        errors = validate_projects(bad)
        assert len(errors) > 0

    def test_validate_all_reports_errors_from_all_sources(self, con_projects, con_cost_lines):
        bad_proj  = con_projects.drop(columns=["payment_status"])
        bad_costs = con_cost_lines.drop(columns=["actual_amount"])
        errors    = validate_all(bad_proj, {"Test Contractor": bad_costs})
        assert len(errors) >= 2
