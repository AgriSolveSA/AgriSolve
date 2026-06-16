"""
Logistics input schema validation.
Single job: validate that uploaded DataFrames have the required columns,
types, and value ranges using pandera.
"""

import os
import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaError, SchemaErrors

os.environ.setdefault("DISABLE_PANDERA_IMPORT_WARNING", "True")

MANIFEST_SCHEMA = pa.DataFrameSchema(
    columns={
        "trip_id":       pa.Column(str),
        "trip_date":     pa.Column(str),
        "vehicle_id":    pa.Column(str),
        "driver":        pa.Column(str),
        "route_id":      pa.Column(str),
        "origin":        pa.Column(str),
        "destination":   pa.Column(str),
        "distance_km":   pa.Column(float, pa.Check.gt(0), coerce=True),
        "fuel_cost":     pa.Column(float, pa.Check.ge(0), coerce=True),
        "toll_cost":     pa.Column(float, pa.Check.ge(0), coerce=True),
        "revenue":       pa.Column(float, pa.Check.ge(0), coerce=True),
        "planned_hours": pa.Column(float, pa.Check.gt(0), coerce=True),
        "actual_hours":  pa.Column(float, pa.Check.gt(0), coerce=True),
        "on_time":       pa.Column(bool, coerce=True),
    },
    coerce=True,
)

FLEET_SCHEMA = pa.DataFrameSchema(
    columns={
        "vehicle_id":   pa.Column(str),
        "vehicle_name": pa.Column(str),
        "insurance":    pa.Column(float, pa.Check.ge(0), coerce=True),
        "maintenance":  pa.Column(float, pa.Check.ge(0), coerce=True),
        "depreciation": pa.Column(float, pa.Check.ge(0), coerce=True),
        "licence_fees": pa.Column(float, pa.Check.ge(0), coerce=True),
    },
    coerce=True,
)

MANIFEST_REQUIRED: frozenset[str] = frozenset(MANIFEST_SCHEMA.columns.keys())
FLEET_REQUIRED: frozenset[str] = frozenset(FLEET_SCHEMA.columns.keys())


def _collect_errors(schema: pa.DataFrameSchema, df: pd.DataFrame, context: str) -> list[str]:
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


def validate_manifest(df: pd.DataFrame) -> list[str]:
    return _collect_errors(MANIFEST_SCHEMA, df, "Trip manifest")


def validate_fleet(name: str, df: pd.DataFrame) -> list[str]:
    return _collect_errors(FLEET_SCHEMA, df, f"Fleet costs '{name}'")


def validate_all(manifest_df: pd.DataFrame, secondaries: dict[str, pd.DataFrame]) -> list[str]:
    errors = validate_manifest(manifest_df)
    for name, df in secondaries.items():
        errors.extend(validate_fleet(name, df))
    return errors
