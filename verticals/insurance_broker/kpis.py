"""
Insurance Broker KPI computations.
Single job: wrap summary_stats and insurer_summary into the VerticalBase contract.
"""

import pandas as pd
from reconcile import (
    summary_stats as _summary_stats,
    insurer_summary as _insurer_summary,
)


def get_summary_stats(
    register_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
    exceptions_df: pd.DataFrame,
) -> dict:
    """
    Return a dict with kpi1..6 _label/_value keys ready for st.metric().
    kpi3 (Net Variance) also provides kpi3_delta and kpi3_positive.
    """
    raw = _summary_stats(register_df, secondaries, exceptions_df)
    var = raw["total_variance"]

    return {
        "kpi1_label": "Expected",
        "kpi1_value": f"R {raw['total_expected']:,.0f}",

        "kpi2_label": "Received",
        "kpi2_value": f"R {raw['total_actual']:,.0f}",

        "kpi3_label":    "Net Variance",
        "kpi3_value":    f"R {abs(var):,.0f}",
        "kpi3_delta":    f"{'▲' if var >= 0 else '▼'} {'surplus' if var >= 0 else 'shortfall'}",
        "kpi3_positive": bool(var >= 0),

        "kpi4_label": "Exceptions",
        "kpi4_value": str(raw["exception_count"]),

        "kpi5_label": "High Priority",
        "kpi5_value": str(raw["high_count"]),

        "kpi6_label": "Total at Risk",
        "kpi6_value": f"R {raw['total_at_risk']:,.0f}",
    }


def get_entity_summary(
    register_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Return per-insurer roll-up with standard columns: entity, expected, actual, variance.
    """
    df = _insurer_summary(register_df, secondaries)
    return df.rename(columns={"insurer": "entity"})
