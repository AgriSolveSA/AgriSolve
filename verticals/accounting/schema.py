"""
Accounting Firm input schema validation.
Single job: validate that uploaded DataFrames have the required columns,
types, and value ranges using pandera.
"""

import os
import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaError, SchemaErrors

os.environ.setdefault("DISABLE_PANDERA_IMPORT_WARNING", "True")

AR_REGISTER_SCHEMA = pa.DataFrameSchema(
    columns={
        "invoice_number":    pa.Column(str),
        "client_name":       pa.Column(str),
        "service_type":      pa.Column(str),
        "invoice_date":      pa.Column(str),
        "due_date":          pa.Column(str),
        "contracted_amount": pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "invoice_amount":    pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "paid_amount":       pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "days_outstanding":  pa.Column(int,   pa.Check.ge(0),   coerce=True),
        "payment_status":    pa.Column(
            str, pa.Check.isin(["Paid", "Partial", "Overdue", "Current"]),
        ),
    },
    coerce=True,
)

REMITTANCE_SCHEMA = pa.DataFrameSchema(
    columns={
        "client_name":       pa.Column(str),
        "invoice_reference": pa.Column(str),
        "payment_date":      pa.Column(str),
        "amount_paid":       pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "payment_method":    pa.Column(str),
    },
    coerce=True,
)

AR_REQUIRED:         frozenset[str] = frozenset(AR_REGISTER_SCHEMA.columns.keys())
REMITTANCE_REQUIRED: frozenset[str] = frozenset(REMITTANCE_SCHEMA.columns.keys())


def _collect_errors(
    schema: pa.DataFrameSchema,
    df: pd.DataFrame,
    context: str,
) -> list[str]:
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
            check = row.get("check")  or "validation failed"
            key   = (col, check)
            if key not in seen:
                seen.add(key)
                msgs.append(f"{context} — column '{col}': {check}")
        return msgs
    except SchemaError as exc:
        return [f"{context} — {exc}"]


def validate_register(df: pd.DataFrame) -> list[str]:
    """Return error strings for the AR register; empty list = valid."""
    return _collect_errors(AR_REGISTER_SCHEMA, df, "AR register")


def validate_remittance(name: str, df: pd.DataFrame) -> list[str]:
    """Return error strings for a client remittance; empty list = valid."""
    return _collect_errors(REMITTANCE_SCHEMA, df, f"Remittance '{name}'")


def validate_all(
    ar_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> list[str]:
    """Validate AR register and all remittance DataFrames."""
    errors = validate_register(ar_df)
    for name, df in secondaries.items():
        errors.extend(validate_remittance(name, df))
    return errors
