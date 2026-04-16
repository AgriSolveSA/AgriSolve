"""
Construction vertical input schema validation.
Single job: validate that uploaded DataFrames have the required columns,
types, and value ranges using pandera.
"""

import os
import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaError, SchemaErrors

os.environ.setdefault("DISABLE_PANDERA_IMPORT_WARNING", "True")

PROJECTS_SCHEMA = pa.DataFrameSchema(
    columns={
        "project_number":   pa.Column(str),
        "project_name":     pa.Column(str),
        "contractor_name":  pa.Column(str),
        "start_date":       pa.Column(str),
        "end_date":         pa.Column(str),
        "contract_value":   pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "budgeted_cost":    pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "actual_cost":      pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "billed_amount":    pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "payment_received": pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "days_outstanding": pa.Column(int,   pa.Check.ge(0),   coerce=True),
        "payment_status":   pa.Column(
            str, pa.Check.isin(["Paid", "Partial", "Overdue", "Current"]),
        ),
    },
    coerce=True,
)

COST_LINES_SCHEMA = pa.DataFrameSchema(
    columns={
        "project_number":  pa.Column(str),
        "contractor_name": pa.Column(str),
        "cost_category":   pa.Column(str),
        "description":     pa.Column(str),
        "budgeted_amount": pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "actual_amount":   pa.Column(float, pa.Check.ge(0.0), coerce=True),
        "invoice_date":    pa.Column(str),
    },
    coerce=True,
)

PROJECTS_REQUIRED:   frozenset[str] = frozenset(PROJECTS_SCHEMA.columns.keys())
COST_LINES_REQUIRED: frozenset[str] = frozenset(COST_LINES_SCHEMA.columns.keys())


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


def validate_projects(df: pd.DataFrame) -> list[str]:
    """Return error strings for the projects register; empty list = valid."""
    return _collect_errors(PROJECTS_SCHEMA, df, "Projects register")


def validate_cost_lines(name: str, df: pd.DataFrame) -> list[str]:
    """Return error strings for a contractor cost-lines sheet; empty list = valid."""
    return _collect_errors(COST_LINES_SCHEMA, df, f"Cost lines '{name}'")


def validate_all(
    projects_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> list[str]:
    """Validate projects register and all contractor cost-line DataFrames."""
    errors = validate_projects(projects_df)
    for name, df in secondaries.items():
        errors.extend(validate_cost_lines(name, df))
    return errors
