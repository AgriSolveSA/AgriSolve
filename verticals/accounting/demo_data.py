"""
Accounting Firm demo data.
Single job: generate deterministic AR register and client remittance DataFrames.

Seeded exceptions (7 total):
  DEBTOR_OVERDUE (High)   — INV-NFC-008, INV-NFC-015, INV-CHL-011
  BANK_MISMATCH  (High)   — INV-BAS-999 (ghost payment, no matching AR record)
  EXPENSE_SPIKE  (Medium) — INV-CHL-016 (advisory fee 133 % above contracted)
  MARGIN_DROP    (Medium) — INV-NFC-010, INV-BAS-006 (partial payments < 85 %)

Total AR rows    : 45 (16 NFC + 16 CHL + 13 BAS)
Total clients    : 3
Total at risk    : R 33,050
"""

import pandas as pd

_NFC = "Ndlovu Farming Co"
_CHL = "Cape Harvest Ltd"
_BAS = "Boland Agri Solutions"

_MONTHS   = list(range(1, 13))   # Jan–Dec
_QUARTERS = [3, 6, 9, 12]        # Mar, Jun, Sep, Dec


def _d(month: int) -> str:
    return f"2025-{month:02d}-01"


def _due(month: int) -> str:
    return f"2025-{month:02d}-28"


def _build_ar_register() -> pd.DataFrame:
    rows: list[dict] = []

    # ── Ndlovu Farming Co — Monthly Bookkeeping (INV-NFC-001..012) ───────────
    for i, m in enumerate(_MONTHS, start=1):
        if m == 8:                               # DEBTOR_OVERDUE
            paid, days, status = 0.0, 90, "Overdue"
        elif m == 10:                            # MARGIN_DROP
            paid, days, status = 5100.0, 30, "Partial"
        else:
            paid, days, status = 8500.0, 0, "Paid"
        rows.append({
            "invoice_number":    f"INV-NFC-{i:03d}",
            "client_name":       _NFC,
            "service_type":      "Monthly Bookkeeping",
            "invoice_date":      _d(m),
            "due_date":          _due(m),
            "contracted_amount": 8500.0,
            "invoice_amount":    8500.0,
            "paid_amount":       paid,
            "days_outstanding":  days,
            "payment_status":    status,
        })

    # ── Ndlovu Farming Co — Quarterly Tax (INV-NFC-013..016) ────────────────
    for j, q in enumerate(_QUARTERS, start=13):
        if q == 9:                               # DEBTOR_OVERDUE
            paid, days, status = 0.0, 75, "Overdue"
        else:
            paid, days, status = 4200.0, 0, "Paid"
        rows.append({
            "invoice_number":    f"INV-NFC-{j:03d}",
            "client_name":       _NFC,
            "service_type":      "Quarterly Tax",
            "invoice_date":      _d(q),
            "due_date":          _due(q),
            "contracted_amount": 4200.0,
            "invoice_amount":    4200.0,
            "paid_amount":       paid,
            "days_outstanding":  days,
            "payment_status":    status,
        })

    # ── Cape Harvest Ltd — Monthly Bookkeeping (INV-CHL-001..012) ───────────
    for i, m in enumerate(_MONTHS, start=1):
        if m == 11:                              # DEBTOR_OVERDUE
            paid, days, status = 0.0, 65, "Overdue"
        else:
            paid, days, status = 7200.0, 0, "Paid"
        rows.append({
            "invoice_number":    f"INV-CHL-{i:03d}",
            "client_name":       _CHL,
            "service_type":      "Monthly Bookkeeping",
            "invoice_date":      _d(m),
            "due_date":          _due(m),
            "contracted_amount": 7200.0,
            "invoice_amount":    7200.0,
            "paid_amount":       paid,
            "days_outstanding":  days,
            "payment_status":    status,
        })

    # ── Cape Harvest Ltd — Quarterly Advisory (INV-CHL-013..016) ────────────
    for j, q in enumerate(_QUARTERS, start=13):
        if q == 12:                              # EXPENSE_SPIKE
            inv_amt, paid = 8400.0, 8400.0
        else:
            inv_amt, paid = 3600.0, 3600.0
        rows.append({
            "invoice_number":    f"INV-CHL-{j:03d}",
            "client_name":       _CHL,
            "service_type":      "Quarterly Advisory",
            "invoice_date":      _d(q),
            "due_date":          _due(q),
            "contracted_amount": 3600.0,
            "invoice_amount":    inv_amt,
            "paid_amount":       paid,
            "days_outstanding":  0,
            "payment_status":    "Paid",
        })

    # ── Boland Agri Solutions — Monthly Bookkeeping (INV-BAS-001..012) ──────
    for i, m in enumerate(_MONTHS, start=1):
        if m == 6:                               # MARGIN_DROP
            paid, days, status = 3100.0, 30, "Partial"
        else:
            paid, days, status = 6200.0, 0, "Paid"
        rows.append({
            "invoice_number":    f"INV-BAS-{i:03d}",
            "client_name":       _BAS,
            "service_type":      "Monthly Bookkeeping",
            "invoice_date":      _d(m),
            "due_date":          _due(m),
            "contracted_amount": 6200.0,
            "invoice_amount":    6200.0,
            "paid_amount":       paid,
            "days_outstanding":  days,
            "payment_status":    status,
        })

    # ── Boland Agri Solutions — Annual Audit (INV-BAS-013) ──────────────────
    rows.append({
        "invoice_number":    "INV-BAS-013",
        "client_name":       _BAS,
        "service_type":      "Annual Audit",
        "invoice_date":      "2025-06-01",
        "due_date":          "2025-06-28",
        "contracted_amount": 22000.0,
        "invoice_amount":    22000.0,
        "paid_amount":       22000.0,
        "days_outstanding":  0,
        "payment_status":    "Paid",
    })

    return pd.DataFrame(rows)


def _build_remittances(ar_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rems: dict[str, list[dict]] = {_NFC: [], _CHL: [], _BAS: []}

    for _, row in ar_df.iterrows():
        if row["paid_amount"] <= 0:
            continue                             # no remittance for zero-paid invoices
        rems[row["client_name"]].append({
            "client_name":       row["client_name"],
            "invoice_reference": row["invoice_number"],
            "payment_date":      row["due_date"],
            "amount_paid":       float(row["paid_amount"]),
            "payment_method":    "EFT",
        })

    # Ghost payment — BANK_MISMATCH: invoice reference not in AR register
    rems[_BAS].append({
        "client_name":       _BAS,
        "invoice_reference": "INV-BAS-999",
        "payment_date":      "2025-06-28",
        "amount_paid":       1850.0,
        "payment_method":    "EFT",
    })

    return {client: pd.DataFrame(rows) for client, rows in rems.items()}


def generate_demo() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Return (ar_df, {client_name: remittance_df})."""
    ar_df = _build_ar_register()
    return ar_df, _build_remittances(ar_df)
