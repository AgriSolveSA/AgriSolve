"""
Insurance Broker input schema validation.
Single job: validate that uploaded DataFrames have the required columns,
types, and value ranges using pandera.
"""

import os
import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaError, SchemaErrors

# Suppress the pandera top-level import FutureWarning at module load
os.environ.setdefault("DISABLE_PANDERA_IMPORT_WARNING", "True")

REGISTER_SCHEMA = pa.DataFrameSchema(
    columns={
        "policy_number":               pa.Column(str),
        "insurer_name":                pa.Column(str),
        "client_surname":              pa.Column(str),
        "client_initials":             pa.Column(str),
        "product_type":                pa.Column(str),
        "policy_status":               pa.Column(
            str, pa.Check.isin(["Active", "Lapsed", "Cancelled"]),
        ),
        "agreed_commission_rate":      pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "monthly_premium":             pa.Column(int, pa.Check.gt(0), coerce=True),
        "expected_monthly_commission": pa.Column(float, pa.Check.ge(0.0), coerce=True),
    },
    coerce=True,
)

STATEMENT_SCHEMA = pa.DataFrameSchema(
    columns={
        "policy_number":     pa.Column(str),
        "insurer_name":      pa.Column(str),
        "client_surname":    pa.Column(str),
        "client_initials":   pa.Column(str),
        "product_type":      pa.Column(str),
        "commission_type":   pa.Column(str),
        "monthly_premium":   pa.Column(int, pa.Check.gt(0), coerce=True),
        "commission_rate":   pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "commission_amount": pa.Column(float, pa.Check.ge(0.0), coerce=True),
    },
    coerce=True,
)

REGISTER_REQUIRED: frozenset[str] = frozenset(REGISTER_SCHEMA.columns.keys())
STATEMENT_REQUIRED: frozenset[str] = frozenset(STATEMENT_SCHEMA.columns.keys())


def _collect_errors(
    schema: pa.DataFrameSchema,
    df: pd.DataFrame,
    context: str,
) -> list[str]:
    """Run schema validation and return human-readable error strings."""
    # Check for missing columns first — gives a clean message before pandera runs
    missing = frozenset(schema.columns.keys()) - set(df.columns)
    if missing:
        return [f"{context} is missing column(s): {', '.join(sorted(missing))}"]

    try:
        schema.validate(df, lazy=True)
        return []
    except SchemaErrors as exc:
        seen: set[tuple] = set()
        msgs: list[str] = []
        for _, row in exc.failure_cases.iterrows():
            col   = row.get("column") or "schema"
            check = row.get("check") or "validation failed"
            key   = (col, check)
            if key not in seen:
                seen.add(key)
                msgs.append(f"{context} — column '{col}': {check}")
        return msgs
    except SchemaError as exc:
        return [f"{context} — {exc}"]


def validate_register(df: pd.DataFrame) -> list[str]:
    """Return error strings for the policy register; empty list = valid."""
    return _collect_errors(REGISTER_SCHEMA, df, "Policy register")


def validate_statement(name: str, df: pd.DataFrame) -> list[str]:
    """Return error strings for a commission statement; empty list = valid."""
    return _collect_errors(STATEMENT_SCHEMA, df, f"Statement '{name}'")


def validate_all(
    register_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> list[str]:
    """Validate register and all statement DataFrames. Returns every error found."""
    errors = validate_register(register_df)
    for name, df in secondaries.items():
        errors.extend(validate_statement(name, df))
    return errors
