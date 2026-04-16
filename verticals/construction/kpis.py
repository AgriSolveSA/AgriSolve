"""
Construction vertical KPI computations.
Single job: wrap projects register aggregations into the VerticalBase contract.
"""

import pandas as pd


def get_summary_stats(
    projects_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
    exceptions_df: pd.DataFrame,
) -> dict:
    """
    Return a dict with kpi1..6 _label/_value keys ready for st.metric().
    kpi3 (Net Outstanding) also provides kpi3_delta and kpi3_positive.
    """
    total_contract  = float(projects_df["contract_value"].sum())
    total_received  = float(projects_df["payment_received"].sum())
    net_variance    = total_received - total_contract  # negative = money outstanding

    exception_count = len(exceptions_df)
    high_count      = int((exceptions_df["severity"] == "High").sum()) if not exceptions_df.empty else 0
    total_at_risk   = float(exceptions_df["variance"].abs().sum())     if not exceptions_df.empty else 0.0

    return {
        "kpi1_label": "Total Contract Value",
        "kpi1_value": f"R {total_contract:,.0f}",

        "kpi2_label": "Total Received",
        "kpi2_value": f"R {total_received:,.0f}",

        "kpi3_label":    "Net Outstanding",
        "kpi3_value":    f"R {abs(net_variance):,.0f}",
        "kpi3_delta":    f"{'▲' if net_variance >= 0 else '▼'} {'surplus' if net_variance >= 0 else 'outstanding'}",
        "kpi3_positive": bool(net_variance >= 0),

        "kpi4_label": "Exceptions",
        "kpi4_value": str(exception_count),

        "kpi5_label": "High Priority",
        "kpi5_value": str(high_count),

        "kpi6_label": "Total at Risk",
        "kpi6_value": f"R {total_at_risk:,.0f}",
    }


def get_entity_summary(
    projects_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Return per-contractor roll-up with standard columns: entity, expected, actual, variance.
    expected = total contract value, actual = total payment received.
    """
    grouped = (
        projects_df
        .groupby("contractor_name", sort=False)
        .agg(
            expected=("contract_value",   "sum"),
            actual=  ("payment_received", "sum"),
        )
        .reset_index()
        .rename(columns={"contractor_name": "entity"})
    )
    grouped["variance"] = grouped["actual"] - grouped["expected"]
    return grouped
