"""
Insurance Broker demo data.
Single job: provide demo DataFrames for the Insurance Broker vertical.

Delegates entirely to the root generate_demo_data module so the seeded
discrepancies and data shapes are defined in one place.
"""

import pandas as pd
from generate_demo_data import generate_demo as _root_generate_demo


def generate_demo() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Return (register_df, {insurer_name: statement_df})."""
    return _root_generate_demo()
