"""
Commission reconciliation engine.
Uses DuckDB to join the policy register against insurer statements
and surface every exception with type, severity, and variance.
"""

import duckdb
import pandas as pd


# Variance threshold below which a mismatch is ignored (rounding noise)
TOLERANCE_PCT = 0.02   # 2 %
SEVERITY_HIGH_PCT = 0.10


def reconcile(
    register_df: pd.DataFrame,
    statements: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Parameters
    ----------
    register_df : broker's policy register (one row per policy)
    statements  : {insurer_name: commission_statement_df}

    Returns
    -------
    DataFrame of exceptions only, sorted by severity then absolute variance.
    Empty DataFrame if no exceptions found.
    """
    if not statements:
        return pd.DataFrame()

    all_stmt = pd.concat(statements.values(), ignore_index=True)

    con = duckdb.connect()
    con.register("reg", register_df)
    con.register("stmt", all_stmt)

    exceptions = con.execute(f"""
        WITH

        -- 1. Match register rows to statement rows
        joined AS (
            SELECT
                r.policy_number,
                r.insurer_name,
                r.client_surname || ' ' || r.client_initials          AS client,
                r.product_type,
                r.policy_status,
                r.agreed_commission_rate                               AS agreed_rate,
                r.monthly_premium                                      AS register_premium,
                r.expected_monthly_commission                          AS expected,
                s.commission_amount                                    AS actual,
                s.commission_rate                                      AS paid_rate,
                s.monthly_premium                                      AS paid_premium,
                COALESCE(s.commission_amount, 0.0)
                    - r.expected_monthly_commission                    AS variance
            FROM reg r
            LEFT JOIN stmt s USING (policy_number, insurer_name)
        ),

        -- 2. Payments from insurer for policies not in our register
        ghosts AS (
            SELECT
                s.policy_number,
                s.insurer_name,
                s.client_surname || ' ' || s.client_initials          AS client,
                s.product_type,
                'UNKNOWN'                                              AS policy_status,
                NULL::DOUBLE                                           AS agreed_rate,
                NULL::INTEGER                                          AS register_premium,
                0.0                                                    AS expected,
                s.commission_amount                                    AS actual,
                s.commission_rate                                      AS paid_rate,
                s.monthly_premium                                      AS paid_premium,
                -s.commission_amount                                   AS variance
            FROM stmt s
            LEFT JOIN reg r USING (policy_number, insurer_name)
            WHERE r.policy_number IS NULL
        ),

        all_rows AS (
            SELECT * FROM joined
            UNION ALL
            SELECT * FROM ghosts
        ),

        -- 3. Classify each row
        classified AS (
            SELECT *,
                CASE
                    WHEN actual IS NULL
                        AND policy_status = 'Active'
                        AND expected > 0
                        THEN 'MISSING_COMMISSION'
                    WHEN policy_status IN ('Lapsed', 'Cancelled')
                        AND COALESCE(actual, 0) > 0
                        THEN 'INVALID_POLICY_PAID'
                    WHEN policy_status = 'UNKNOWN'
                        THEN 'GHOST_POLICY'
                    WHEN actual IS NOT NULL
                        AND ABS(variance) / NULLIF(expected, 0) > {TOLERANCE_PCT}
                        THEN 'RATE_MISMATCH'
                    ELSE 'OK'
                END AS exception_type,

                CASE
                    WHEN actual IS NULL
                        AND policy_status = 'Active'
                        AND expected > 0
                        THEN 'High'
                    WHEN policy_status IN ('Lapsed', 'Cancelled')
                        AND COALESCE(actual, 0) > 0
                        THEN 'High'
                    WHEN policy_status = 'UNKNOWN'
                        THEN 'Medium'
                    WHEN actual IS NOT NULL
                        AND ABS(variance) / NULLIF(expected, 0) > {SEVERITY_HIGH_PCT}
                        THEN 'High'
                    WHEN actual IS NOT NULL
                        AND ABS(variance) / NULLIF(expected, 0) > {TOLERANCE_PCT}
                        THEN 'Medium'
                    ELSE 'Low'
                END AS severity
            FROM all_rows
        )

        SELECT
            policy_number,
            insurer_name,
            client,
            product_type,
            policy_status,
            ROUND(agreed_rate * 100, 2)     AS agreed_rate_pct,
            ROUND(paid_rate * 100, 2)       AS paid_rate_pct,
            register_premium,
            paid_premium,
            ROUND(expected, 2)              AS expected,
            ROUND(COALESCE(actual, 0), 2)   AS actual,
            ROUND(variance, 2)              AS variance,
            exception_type,
            severity
        FROM classified
        WHERE exception_type != 'OK'
        ORDER BY
            CASE severity WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
            ABS(variance) DESC
    """).df()

    con.close()
    return exceptions


def summary_stats(
    register_df: pd.DataFrame,
    statements: dict[str, pd.DataFrame],
    exceptions_df: pd.DataFrame,
) -> dict:
    """
    High-level KPIs for the dashboard header cards.
    """
    all_stmt = pd.concat(statements.values(), ignore_index=True) if statements else pd.DataFrame()

    total_expected = register_df["expected_monthly_commission"].sum()
    total_actual   = all_stmt["commission_amount"].sum() if not all_stmt.empty else 0.0
    total_variance = total_actual - total_expected

    exc = exceptions_df
    # Money the insurer still owes us (underpaid or missing)
    recoverable = exc.loc[
        exc["exception_type"].isin(["MISSING_COMMISSION", "RATE_MISMATCH"]) &
        (exc["variance"] < 0),
        "variance"
    ].abs().sum()
    # All exception amounts combined (total disputes to raise)
    total_at_risk = exc["variance"].abs().sum()

    return {
        "total_expected":  round(total_expected, 2),
        "total_actual":    round(total_actual,   2),
        "total_variance":  round(total_variance, 2),
        "exception_count": len(exc),
        "high_count":      int((exc["severity"] == "High").sum()),
        "recoverable":     round(recoverable, 2),
        "total_at_risk":   round(total_at_risk, 2),
    }


def insurer_summary(
    register_df: pd.DataFrame,
    statements: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Per-insurer expected vs actual commission — used for the waterfall chart.
    """
    rows = []
    for insurer, stmt_df in statements.items():
        expected = register_df.loc[
            (register_df["insurer_name"] == insurer) &
            (register_df["policy_status"] == "Active"),
            "expected_monthly_commission"
        ].sum()
        actual = stmt_df["commission_amount"].sum()
        rows.append({
            "insurer":  insurer,
            "expected": round(expected, 2),
            "actual":   round(actual,   2),
            "variance": round(actual - expected, 2),
        })
    return pd.DataFrame(rows)
