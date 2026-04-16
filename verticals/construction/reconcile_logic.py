"""
Construction vertical reconciliation logic.
Single job: cross-reference the projects register against cost thresholds using
DuckDB and return exceptions in the VerticalBase standard column format.

Exception types
---------------
COST_OVERRUN  (High)    actual_cost > budgeted_cost * 1.1
SLOW_PAYMENT  (High)    days_outstanding > 45 with Overdue/Partial status
MARGIN_EROSION (Medium)  (contract_value - actual_cost) / contract_value < 0.10
"""

import duckdb
import pandas as pd

_OVERRUN_MULTIPLIER = 1.1    # actual > budget * 1.1  → COST_OVERRUN
_PAYMENT_DAYS       = 45     # days outstanding > 45  → SLOW_PAYMENT
_MARGIN_THRESHOLD   = 0.10   # gross margin < 10 %    → MARGIN_EROSION


def run_reconciliation(
    projects_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Parameters
    ----------
    projects_df : projects register (one row per project)
    secondaries : {contractor_name: cost_lines_df}  (used for entity summary; not
                  required for exception detection — all exceptions derive from
                  projects_df so this function works with an empty dict)

    Returns
    -------
    DataFrame of exceptions only, sorted by severity then absolute variance.
    Standard columns: entity_id, counterparty, description,
                      exception_type, severity, variance
    """
    con = duckdb.connect()
    con.register("projects", projects_df)

    exceptions = con.execute(f"""
        WITH

        -- 1. Actual cost exceeded budget by more than 10 %
        cost_overrun AS (
            SELECT
                project_number                  AS entity_id,
                contractor_name                 AS counterparty,
                project_name                    AS description,
                actual_cost - budgeted_cost     AS variance,
                'COST_OVERRUN'                  AS exception_type,
                'High'                          AS severity
            FROM projects
            WHERE actual_cost > budgeted_cost * {_OVERRUN_MULTIPLIER}
        ),

        -- 2. Payment outstanding beyond the threshold window
        slow_payment AS (
            SELECT
                project_number                          AS entity_id,
                contractor_name                         AS counterparty,
                project_name                            AS description,
                payment_received - billed_amount        AS variance,
                'SLOW_PAYMENT'                          AS exception_type,
                'High'                                  AS severity
            FROM projects
            WHERE days_outstanding > {_PAYMENT_DAYS}
              AND payment_status IN ('Overdue', 'Partial')
              AND project_number NOT IN (SELECT entity_id FROM cost_overrun)
        ),

        -- 3. Gross margin below minimum threshold (excludes cost overruns and slow payments)
        margin_erosion AS (
            SELECT
                project_number                                              AS entity_id,
                contractor_name                                             AS counterparty,
                project_name                                                AS description,
                (contract_value - actual_cost)
                    - contract_value * {_MARGIN_THRESHOLD}                 AS variance,
                'MARGIN_EROSION'                                            AS exception_type,
                'Medium'                                                    AS severity
            FROM projects
            WHERE contract_value > 0
              AND (contract_value - actual_cost) / contract_value < {_MARGIN_THRESHOLD}
              AND project_number NOT IN (SELECT entity_id FROM cost_overrun)
              AND project_number NOT IN (SELECT entity_id FROM slow_payment)
        )

        SELECT * FROM (
            SELECT * FROM cost_overrun
            UNION ALL SELECT * FROM slow_payment
            UNION ALL SELECT * FROM margin_erosion
        ) combined
        ORDER BY
            CASE severity WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
            ABS(variance) DESC

    """).df()

    con.close()
    return exceptions
