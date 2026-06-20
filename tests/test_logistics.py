"""
Logistics vertical tests — mirrors test_insurance_broker.py structure.
"""

import pytest
import pandas as pd
from verticals.logistics.demo_data import generate_demo
from verticals.logistics.schema import validate_all, validate_manifest, validate_fleet, MANIFEST_REQUIRED, FLEET_REQUIRED
from verticals.logistics.reconcile_logic import run_reconciliation
from verticals.logistics.kpis import get_summary_stats, get_entity_summary
from verticals.logistics.vertical import LogisticsVertical


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def demo():
    return generate_demo()


@pytest.fixture(scope="module")
def manifest_df(demo):
    return demo[0]


@pytest.fixture(scope="module")
def secondaries(demo):
    return demo[1]


@pytest.fixture(scope="module")
def exceptions_df(manifest_df, secondaries):
    return run_reconciliation(manifest_df, secondaries)


# ── Demo data ──────────────────────────────────────────────────────────────────

def test_demo_returns_tuple(demo):
    assert isinstance(demo, tuple) and len(demo) == 2


def test_manifest_is_dataframe(manifest_df):
    assert isinstance(manifest_df, pd.DataFrame)


def test_manifest_has_required_columns(manifest_df):
    missing = MANIFEST_REQUIRED - set(manifest_df.columns)
    assert not missing, f"Manifest missing columns: {missing}"


def test_generate_demo_is_stable_across_repeated_calls_in_the_same_process():
    # Regression: the module-level `_RNG = np.random.default_rng(42)` only
    # fixed the *first* call's output. Streamlit reruns the whole script
    # (including this call) on every widget interaction within a session, so
    # the old version silently produced a different random manifest on every
    # click -- numbers and exceptions would visibly shuffle on screen with
    # no actual change, breaking a live sales demo's credibility.
    manifest_a, fleet_a = generate_demo()
    manifest_b, fleet_b = generate_demo()
    assert manifest_a.equals(manifest_b)
    assert fleet_a["fleet_costs"].equals(fleet_b["fleet_costs"])


def test_manifest_has_rows(manifest_df):
    assert len(manifest_df) > 10


def test_secondaries_has_fleet_key(secondaries):
    assert "fleet_costs" in secondaries


def test_fleet_has_required_columns(secondaries):
    fleet_df = secondaries["fleet_costs"]
    missing = FLEET_REQUIRED - set(fleet_df.columns)
    assert not missing, f"Fleet sheet missing columns: {missing}"


def test_fleet_has_four_vehicles(secondaries):
    assert len(secondaries["fleet_costs"]) == 4


def test_demo_seeds_exceptions(manifest_df):
    variable_cost = manifest_df["fuel_cost"] + manifest_df["toll_cost"]
    loss_rows = manifest_df[manifest_df["revenue"] < variable_cost]
    assert len(loss_rows) > 0, "Expected at least one seeded loss-making trip"


# ── Schema validation ──────────────────────────────────────────────────────────

def test_valid_manifest_passes(manifest_df, secondaries):
    errors = validate_all(manifest_df, secondaries)
    assert errors == [], f"Unexpected errors: {errors}"


def test_missing_column_caught(manifest_df, secondaries):
    bad = manifest_df.drop(columns=["revenue"])
    errors = validate_manifest(bad)
    assert any("revenue" in e for e in errors)


def test_negative_distance_caught(manifest_df):
    bad = manifest_df.copy()
    bad.at[0, "distance_km"] = -10
    errors = validate_manifest(bad)
    assert any("distance_km" in e for e in errors)


def test_fleet_missing_column_caught(secondaries):
    fleet_df = secondaries["fleet_costs"].drop(columns=["insurance"])
    errors = validate_fleet("fleet_costs", fleet_df)
    assert any("insurance" in e for e in errors)


# ── Reconciliation ─────────────────────────────────────────────────────────────

def test_reconciliation_returns_dataframe(exceptions_df):
    assert isinstance(exceptions_df, pd.DataFrame)


def test_exceptions_have_required_columns(exceptions_df):
    required = {"entity_id", "counterparty", "description", "exception_type", "severity", "variance"}
    missing = required - set(exceptions_df.columns)
    assert not missing, f"Exceptions missing: {missing}"


def test_loss_making_exceptions_detected(exceptions_df):
    loss = exceptions_df[exceptions_df["exception_type"] == "LOSS_MAKING_TRIP"]
    assert len(loss) > 0, "Expected loss-making trip exceptions"


def test_late_delivery_exceptions_detected(exceptions_df):
    late = exceptions_df[exceptions_df["exception_type"] == "LATE_DELIVERY"]
    assert len(late) > 0, "Expected late delivery exceptions"


def test_severity_values_valid(exceptions_df):
    valid = {"High", "Medium", "Low"}
    assert set(exceptions_df["severity"].unique()).issubset(valid)


def test_no_exceptions_on_clean_data():
    manifest = pd.DataFrame([{
        "trip_id": "TR-0001", "trip_date": "2026-03-01", "vehicle_id": "VEH-001",
        "driver": "J. Dlamini", "route_id": "RT-JHB-DBN",
        "origin": "Johannesburg", "destination": "Durban", "distance_km": 590.0,
        "fuel_cost": 500.0, "toll_cost": 100.0, "revenue": 5000.0,
        "planned_hours": 7.0, "actual_hours": 7.2, "on_time": True,
    }])
    fleet = pd.DataFrame([{
        "vehicle_id": "VEH-001", "vehicle_name": "Toyota Hino",
        "insurance": 4000, "maintenance": 3000, "depreciation": 5000, "licence_fees": 850,
    }])
    result = run_reconciliation(manifest, {"fleet_costs": fleet})
    assert len(result) == 0, "Clean trip should produce no exceptions"


# ── KPIs ───────────────────────────────────────────────────────────────────────

def test_summary_stats_returns_dict(manifest_df, secondaries, exceptions_df):
    stats = get_summary_stats(manifest_df, secondaries, exceptions_df)
    assert isinstance(stats, dict)


def test_summary_stats_has_six_kpis(manifest_df, secondaries, exceptions_df):
    stats = get_summary_stats(manifest_df, secondaries, exceptions_df)
    for i in range(1, 7):
        assert f"kpi{i}_label" in stats
        assert f"kpi{i}_value" in stats


def test_kpi3_has_delta_and_positive(manifest_df, secondaries, exceptions_df):
    stats = get_summary_stats(manifest_df, secondaries, exceptions_df)
    assert "kpi3_delta" in stats
    assert isinstance(stats["kpi3_positive"], bool)


def test_entity_summary_returns_dataframe(manifest_df, secondaries):
    df = get_entity_summary(manifest_df, secondaries)
    assert isinstance(df, pd.DataFrame)


def test_entity_summary_has_required_columns(manifest_df, secondaries):
    df = get_entity_summary(manifest_df, secondaries)
    for col in ("entity", "expected", "actual"):
        assert col in df.columns, f"Missing column: {col}"


def test_entity_summary_one_row_per_vehicle(manifest_df, secondaries):
    df = get_entity_summary(manifest_df, secondaries)
    assert len(df) == manifest_df["vehicle_id"].nunique()


# ── VerticalBase contract ──────────────────────────────────────────────────────

def test_vertical_name():
    assert LogisticsVertical().name == "Logistics"


def test_vertical_icon():
    assert LogisticsVertical().icon == "🚛"


def test_vertical_primary_entity_label():
    assert LogisticsVertical().primary_entity_label == "Trip"


def test_vertical_counterparty_label():
    assert LogisticsVertical().counterparty_label == "Vehicle"


def test_upload_labels_has_required_keys():
    labels = LogisticsVertical().get_upload_labels()
    required = {
        "primary_label", "primary_caption", "secondary_label",
        "secondary_caption", "demo_caption", "secondary_key_column",
    }
    assert required.issubset(set(labels.keys()))


def test_recovery_tracker_has_required_keys():
    tracker = LogisticsVertical().get_recovery_tracker_label()
    required = {
        "prior_section", "current_section",
        "disputed_label", "disputed_value",
        "recovered_label", "recovered_value", "recovered_delta",
        "pending_label", "pending_value",
        "prior_rows", "entity_noun", "counterparty_noun",
    }
    assert required.issubset(set(tracker.keys()))
    assert isinstance(tracker["prior_rows"], list) and len(tracker["prior_rows"]) > 0
