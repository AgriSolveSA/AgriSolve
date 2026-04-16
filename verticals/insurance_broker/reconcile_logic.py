"""
Insurance Broker reconciliation logic.
Single job: run the DuckDB reconciliation and return exceptions in the
VerticalBase standard column format.
"""

import pandas as pd
from reconcile import reconcile as _root_reconcile

# Standard output columns required by VerticalBase.run_reconciliation()
_RENAME = {
    "policy_number": "entity_id",
    "insurer_name":  "counterparty",
    "client":        "description",
}


def run_reconciliation(
    register_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Call root reconcile() and remap to the VerticalBase standard columns:
        entity_id, counterparty, description, exception_type, severity, variance

    Additional display columns are preserved:
        product_type, policy_status, agreed_rate_pct, paid_rate_pct,
        register_premium, paid_premium, expected, actual
    """
    df = _root_reconcile(register_df, secondaries)
    return df.rename(columns=_RENAME)
