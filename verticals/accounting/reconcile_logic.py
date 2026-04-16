"""
Accounting Firm reconciliation logic.
Single job: cross-reference the AR register against client remittances using
DuckDB and return exceptions in the VerticalBase standard column format.

Exception types
---------------
DEBTOR_OVERDUE  (High)   days_outstanding > 60 with Overdue/Partial status
BANK_MISMATCH   (High)   remittance references an invoice not in AR register
EXPENSE_SPIKE   (Medium) invoice_amount > contracted_amount * 1.5
MARGIN_DROP     (Medium) paid_amount < invoice_amount * 0.85, within 60 days
"""

import duckdb
import pandas as pd

_OVERDUE_DAYS      = 60
_SPIKE_MULTIPLIER  = 1.5
_MARGIN_THRESHOLD  = 0.85


def run_reconciliation(
    ar_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Parameters
    ----------
    ar_df       : accounts-receivable register (one row per invoice)
    secondaries : {client_name: remittance_df}

    Returns
    -------
    DataFrame of exceptions only, sorted by severity then absolute variance.
    Standard columns: entity_id, counterparty, description,
                      exception_type, severity, variance
    """
    if not secondaries:
        return pd.DataFrame()

    all_rem = pd.concat(secondaries.values(), ignore_index=True)

    con = duckdb.connect()
    con.register("ar",  ar_df)
    con.register("rem", all_rem)

    exceptions = con.execute(f"""
        WITH

        -- 1. Invoices past the overdue threshold
        debtor_overdue AS (
            SELECT
                invoice_number               AS entity_id,
                client_name                  AS counterparty,
                service_type                 AS description,
                paid_amount - invoice_amount AS variance,
                'DEBTOR_OVERDUE'             AS exception_type,
                'High'                       AS severity
            FROM ar
            WHERE days_outstanding > {_OVERDUE_DAYS}
              AND payment_status IN ('Overdue', 'Partial')
        ),

        -- 2. Invoiced amount significantly above the contracted fee
        expense_spike AS (
            SELECT
                invoice_number                     AS entity_id,
                client_name                        AS counterparty,
                service_type                       AS description,
                invoice_amount - contracted_amount AS variance,
                'EXPENSE_SPIKE'                    AS exception_type,
                'Medium'                           AS severity
            FROM ar
            WHERE invoice_amount > contracted_amount * {_SPIKE_MULTIPLIER}
              AND invoice_number NOT IN (SELECT entity_id FROM debtor_overdue)
        ),

        -- 3. Partial payment below 85 % of invoice, still within overdue window
        margin_drop AS (
            SELECT
                invoice_number               AS entity_id,
                client_name                  AS counterparty,
                service_type                 AS description,
                paid_amount - invoice_amount AS variance,
                'MARGIN_DROP'                AS exception_type,
                'Medium'                     AS severity
            FROM ar
            WHERE paid_amount < invoice_amount * {_MARGIN_THRESHOLD}
              AND days_outstanding <= {_OVERDUE_DAYS}
              AND invoice_number NOT IN (SELECT entity_id FROM debtor_overdue)
              AND invoice_number NOT IN (SELECT entity_id FROM expense_spike)
        ),

        -- 4. Remittance payment with no matching AR invoice
        bank_mismatch AS (
            SELECT
                r.invoice_reference AS entity_id,
                r.client_name       AS counterparty,
                'Unmatched payment' AS description,
                -r.amount_paid      AS variance,
                'BANK_MISMATCH'     AS exception_type,
                'High'              AS severity
            FROM rem r
            LEFT JOIN ar ON r.invoice_reference = ar.invoice_number
            WHERE ar.invoice_number IS NULL
        )

        SELECT * FROM (
            SELECT * FROM debtor_overdue
            UNION ALL SELECT * FROM expense_spike
            UNION ALL SELECT * FROM margin_drop
            UNION ALL SELECT * FROM bank_mismatch
        ) combined
        ORDER BY
            CASE severity WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
            ABS(variance) DESC

    """).df()

    con.close()
    return exceptions
