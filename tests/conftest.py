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


# ── Accounting Firm fixtures ──────────────────────────────────────────────────

@pytest.fixture
def acc_register() -> pd.DataFrame:
    """Minimal 3-row valid AR register for the Accounting Firm vertical."""
    rows = []
    for i in range(1, 4):
        rows.append({
            "invoice_number":    f"INV-TEST-{i:03d}",
            "client_name":       "Test Client",
            "service_type":      "Monthly Bookkeeping",
            "invoice_date":      "2025-01-01",
            "due_date":          "2025-01-28",
            "contracted_amount": 5000.0,
            "invoice_amount":    5000.0,
            "paid_amount":       5000.0,
            "days_outstanding":  0,
            "payment_status":    "Paid",
        })
    return pd.DataFrame(rows)


@pytest.fixture
def acc_remittance() -> pd.DataFrame:
    """Minimal 3-row valid remittance for the Accounting Firm vertical."""
    rows = []
    for i in range(1, 4):
        rows.append({
            "client_name":       "Test Client",
            "invoice_reference": f"INV-TEST-{i:03d}",
            "payment_date":      "2025-01-28",
            "amount_paid":       5000.0,
            "payment_method":    "EFT",
        })
    return pd.DataFrame(rows)


# ── Construction vertical fixtures ───────────────────────────────────────────

@pytest.fixture
def con_projects() -> pd.DataFrame:
    """Minimal 3-row valid projects register for the Construction vertical."""
    rows = []
    for i in range(1, 4):
        rows.append({
            "project_number":   f"PRJ-TEST-{i:03d}",
            "project_name":     f"Test Project {i}",
            "contractor_name":  "Test Contractor",
            "start_date":       "2025-01-01",
            "end_date":         "2025-06-30",
            "contract_value":   100_000.0,
            "budgeted_cost":     80_000.0,
            "actual_cost":       80_000.0,
            "billed_amount":    100_000.0,
            "payment_received": 100_000.0,
            "days_outstanding": 0,
            "payment_status":   "Paid",
        })
    return pd.DataFrame(rows)


@pytest.fixture
def con_cost_lines() -> pd.DataFrame:
    """Minimal 3-row valid cost lines for the Construction vertical."""
    rows = []
    for i in range(1, 4):
        rows.append({
            "project_number":  f"PRJ-TEST-{i:03d}",
            "contractor_name": "Test Contractor",
            "cost_category":   "Labour",
            "description":     "Site labour",
            "budgeted_amount": 80_000.0,
            "actual_amount":   80_000.0,
            "invoice_date":    "2025-06-01",
        })
    return pd.DataFrame(rows)
