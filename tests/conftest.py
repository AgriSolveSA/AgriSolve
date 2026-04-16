"""
Shared fixtures for all AgriSolve SME vertical tests.

Each fixture produces a minimal 5-row valid DataFrame.
Tests mutate copies of these to exercise invalid paths.
"""

import pytest
import pandas as pd


@pytest.fixture
def ib_register() -> pd.DataFrame:
    """Minimal 5-row valid policy register for the Insurance Broker vertical."""
    rows = []
    for i in range(1, 6):
        rows.append({
            "policy_number":               f"POL-{i:04d}",
            "insurer_name":                "Test Insurer",
            "insurer_ref":                 f"TI{i:06d}",
            "client_surname":              "Smith",
            "client_initials":             "AB",
            "product_type":                "Life Cover",
            "policy_status":               "Active",
            "inception_date":              "2023-01-01",
            "agreed_commission_rate":      0.025,
            "monthly_premium":             2000,
            "expected_monthly_commission": 50.0,
        })
    return pd.DataFrame(rows)


@pytest.fixture
def ib_statement() -> pd.DataFrame:
    """Minimal 5-row valid commission statement for the Insurance Broker vertical."""
    rows = []
    for i in range(1, 6):
        rows.append({
            "statement_date":    "2026-03-31",
            "insurer_name":      "Test Insurer",
            "policy_number":     f"POL-{i:04d}",
            "insurer_ref":       f"TI{i:06d}",
            "client_surname":    "Smith",
            "client_initials":   "AB",
            "product_type":      "Life Cover",
            "commission_type":   "Renewal",
            "monthly_premium":   2000,
            "commission_rate":   0.025,
            "commission_amount": 50.0,
        })
    return pd.DataFrame(rows)
