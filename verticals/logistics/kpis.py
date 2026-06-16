"""
Logistics KPI computations.
Single job: wrap fleet metrics into the VerticalBase 6-KPI contract.
"""

import pandas as pd


def get_summary_stats(
    manifest_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
    exceptions_df: pd.DataFrame,
) -> dict:
    total_revenue   = manifest_df["revenue"].sum()
    total_fuel      = manifest_df["fuel_cost"].sum()
    total_toll      = manifest_df["toll_cost"].sum()
    variable_costs  = total_fuel + total_toll
    net_margin      = total_revenue - variable_costs
    total_km        = manifest_df["distance_km"].sum()
    on_time_rate    = manifest_df["on_time"].mean() * 100 if len(manifest_df) else 0
    cost_per_km     = variable_costs / total_km if total_km > 0 else 0
    exception_count = len(exceptions_df) if exceptions_df is not None else 0
    high_count      = len(exceptions_df[exceptions_df["severity"] == "High"]) if exception_count else 0
    margin_at_risk  = abs(exceptions_df[exceptions_df["variance"] < 0]["variance"].sum()) if exception_count else 0

    margin_positive = bool(net_margin >= 0)

    return {
        "kpi1_label": "Total Revenue",
        "kpi1_value": f"R {total_revenue:,.0f}",

        "kpi2_label": "Variable Costs",
        "kpi2_value": f"R {variable_costs:,.0f}",

        "kpi3_label":    "Net Margin",
        "kpi3_value":    f"R {abs(net_margin):,.0f}",
        "kpi3_delta":    f"{'▲' if margin_positive else '▼'} {'surplus' if margin_positive else 'shortfall'}",
        "kpi3_positive": margin_positive,

        "kpi4_label": "On-Time Rate",
        "kpi4_value": f"{on_time_rate:.1f}%",

        "kpi5_label": "Cost / km",
        "kpi5_value": f"R {cost_per_km:.2f}",

        "kpi6_label": "Revenue at Risk",
        "kpi6_value": f"R {margin_at_risk:,.0f}",
    }


def get_entity_summary(
    manifest_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Per-vehicle roll-up: entity, expected (revenue), actual (revenue - variable cost)."""
    df = manifest_df.copy()
    df["variable_cost"] = df["fuel_cost"] + df["toll_cost"]
    grouped = (
        df.groupby("vehicle_id")
        .agg(expected=("revenue", "sum"), actual=("variable_cost", lambda x: df.loc[x.index, "revenue"].sum() - x.sum()))
        .reset_index()
        .rename(columns={"vehicle_id": "entity"})
    )
    grouped["variance"] = grouped["actual"] - grouped["expected"]
    return grouped
