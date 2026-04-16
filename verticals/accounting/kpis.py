"""
Accounting Firm KPI computations.
Single job: wrap AR register aggregations into the VerticalBase contract.
"""

import pandas as pd


def get_summary_stats(
    ar_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
    exceptions_df: pd.DataFrame,
) -> dict:
    """
    Return a dict with kpi1..6 _label/_value keys ready for st.metric().
    kpi3 (Net Outstanding) also provides kpi3_delta and kpi3_positive.
    """
    total_invoiced = float(ar_df["invoice_amount"].sum())
    total_received = float(ar_df["paid_amount"].sum())
    net_variance   = total_received - total_invoiced  # negative = money owed to firm

    exception_count = len(exceptions_df)
    high_count      = int((exceptions_df["severity"] == "High").sum()) if not exceptions_df.empty else 0
    total_at_risk   = float(exceptions_df["variance"].abs().sum())     if not exceptions_df.empty else 0.0

    return {
        "kpi1_label": "Total Invoiced",
        "kpi1_value": f"R {total_invoiced:,.0f}",

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
    ar_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Return per-client roll-up with standard columns: entity, expected, actual, variance.
    """
    grouped = (
        ar_df
        .groupby("client_name", sort=False)
        .agg(
            expected=("invoice_amount", "sum"),
            actual=("paid_amount",   "sum"),
        )
        .reset_index()
        .rename(columns={"client_name": "entity"})
    )
    grouped["variance"] = grouped["actual"] - grouped["expected"]
    return grouped
