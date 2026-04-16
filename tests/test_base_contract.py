"""
ABC contract compliance tests.

For every vertical registered in REGISTRY, verifies:
  - Subclasses VerticalBase
  - Instantiates with no arguments
  - All properties return non-empty strings
  - Every abstract method returns the correct type and satisfies the column contract

These tests use no Streamlit, no mocks, and no vertical-specific knowledge.
"""

import pytest
import pandas as pd

from verticals import REGISTRY
from verticals.base import VerticalBase

# Required dict keys per ABC contract ─────────────────────────────────────────

REQUIRED_STAT_KEYS = {
    "kpi1_label", "kpi1_value",
    "kpi2_label", "kpi2_value",
    "kpi3_label", "kpi3_value", "kpi3_delta", "kpi3_positive",
    "kpi4_label", "kpi4_value",
    "kpi5_label", "kpi5_value",
    "kpi6_label", "kpi6_value",
}

REQUIRED_TRACKER_KEYS = {
    "prior_section", "current_section",
    "disputed_label", "disputed_value",
    "recovered_label", "recovered_value", "recovered_delta",
    "pending_label",  "pending_value",
    "prior_rows",
    "entity_noun", "counterparty_noun",
}

REQUIRED_UPLOAD_KEYS = {
    "primary_label", "primary_caption",
    "secondary_label", "secondary_caption",
    "demo_caption", "secondary_key_column",
}

# Required columns in run_reconciliation() output ─────────────────────────────
STANDARD_EXCEPTION_COLS = frozenset({
    "entity_id", "counterparty", "description",
    "exception_type", "severity", "variance",
})

# Required columns in get_entity_summary() output ─────────────────────────────
ENTITY_SUMMARY_COLS = frozenset({"entity", "expected", "actual"})


# ── Parametrised test class ───────────────────────────────────────────────────
@pytest.mark.parametrize("name,cls", list(REGISTRY.items()))
class TestVerticalContract:

    # Identity ─────────────────────────────────────────────────────────────────

    def test_is_subclass_of_verticalbase(self, name, cls):
        assert issubclass(cls, VerticalBase)

    def test_instantiates_with_no_args(self, name, cls):
        v = cls()
        assert v is not None

    def test_name_is_nonempty_string(self, name, cls):
        v = cls()
        assert isinstance(v.name, str) and v.name.strip()

    def test_icon_is_nonempty_string(self, name, cls):
        v = cls()
        assert isinstance(v.icon, str) and v.icon.strip()

    def test_primary_entity_label_is_nonempty_string(self, name, cls):
        v = cls()
        assert isinstance(v.primary_entity_label, str) and v.primary_entity_label.strip()

    def test_counterparty_label_is_nonempty_string(self, name, cls):
        v = cls()
        assert isinstance(v.counterparty_label, str) and v.counterparty_label.strip()

    # Data ─────────────────────────────────────────────────────────────────────

    def test_generate_demo_returns_dataframe_and_dict(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        assert isinstance(primary_df, pd.DataFrame)
        assert isinstance(secondaries, dict)
        assert len(primary_df) > 0
        assert len(secondaries) > 0

    def test_validate_inputs_returns_list(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        result = v.validate_inputs(primary_df, secondaries)
        assert isinstance(result, list)

    def test_demo_data_passes_validation(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        errors = v.validate_inputs(primary_df, secondaries)
        assert errors == [], f"{name} demo data failed its own validation: {errors}"

    # Reconciliation ───────────────────────────────────────────────────────────

    def test_run_reconciliation_returns_dataframe(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        exc = v.run_reconciliation(primary_df, secondaries)
        assert isinstance(exc, pd.DataFrame)

    def test_run_reconciliation_standard_columns_present(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        exc = v.run_reconciliation(primary_df, secondaries)
        missing = STANDARD_EXCEPTION_COLS - set(exc.columns)
        assert not missing, f"{name} missing standard exception columns: {missing}"

    def test_severity_values_are_valid(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        exc = v.run_reconciliation(primary_df, secondaries)
        if not exc.empty:
            assert set(exc["severity"]).issubset({"High", "Medium", "Low"})

    # Summaries ────────────────────────────────────────────────────────────────

    def test_get_summary_stats_has_required_keys(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        exc = v.run_reconciliation(primary_df, secondaries)
        stats = v.get_summary_stats(primary_df, secondaries, exc)
        missing = REQUIRED_STAT_KEYS - set(stats.keys())
        assert not missing, f"{name} get_summary_stats missing keys: {missing}"

    def test_kpi3_positive_is_bool(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        exc = v.run_reconciliation(primary_df, secondaries)
        stats = v.get_summary_stats(primary_df, secondaries, exc)
        assert isinstance(stats["kpi3_positive"], bool)

    def test_get_entity_summary_has_required_columns(self, name, cls):
        v = cls()
        primary_df, secondaries = v.generate_demo()
        es = v.get_entity_summary(primary_df, secondaries)
        assert isinstance(es, pd.DataFrame)
        missing = ENTITY_SUMMARY_COLS - set(es.columns)
        assert not missing, f"{name} get_entity_summary missing columns: {missing}"

    # UI labels ────────────────────────────────────────────────────────────────

    def test_get_recovery_tracker_label_has_required_keys(self, name, cls):
        v = cls()
        rt = v.get_recovery_tracker_label()
        assert isinstance(rt, dict)
        missing = REQUIRED_TRACKER_KEYS - set(rt.keys())
        assert not missing, f"{name} get_recovery_tracker_label missing keys: {missing}"

    def test_prior_rows_is_a_list(self, name, cls):
        v = cls()
        rt = v.get_recovery_tracker_label()
        assert isinstance(rt["prior_rows"], list)

    def test_get_upload_labels_has_required_keys(self, name, cls):
        v = cls()
        labels = v.get_upload_labels()
        assert isinstance(labels, dict)
        missing = REQUIRED_UPLOAD_KEYS - set(labels.keys())
        assert not missing, f"{name} get_upload_labels missing keys: {missing}"
