# AgriSolve SME — Reconciliation Dashboard

> Multi-vertical data reconciliation and exception reporting for South African SMEs.  
> Delivered as a Streamlit web app. Demo-ready. 4 verticals live.

**Last updated:** 2026-06-16

---

## What This Module Contains

| File/Folder | Purpose |
|-------------|---------|
| `app.py` | Streamlit app — all pages, period selector, Excel export, email digest |
| `verticals/` | Plugin registry — one sub-package per business vertical |
| `verticals/base.py` | Abstract base class all verticals must implement |
| `verticals/insurance_broker/` | Insurance Broker vertical (schema, demo data, reconcile, KPIs) |
| `verticals/accounting/` | Accounting Firm vertical |
| `verticals/construction/` | Construction vertical |
| `verticals/logistics/` | Logistics vertical |
| `tests/` | Pytest suite — 6 files, full coverage per vertical |
| `.streamlit/config.toml` | Dark theme, port 8501 |
| `.streamlit/secrets.toml.example` | SMTP config template — copy to `secrets.toml` to enable email |
| `generate_demo_data.py` | CLI to generate demo CSV files |
| `reconcile.py` | CLI reconciliation runner |

---

## Run the Dashboard

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## Features

### Three pages

| Page | What it does |
|------|-------------|
| Overview | 6-card KPI row + expected vs received bar chart + exception breakdown charts |
| Exception Report | Filtered table with severity highlighting, CSV + Excel download |
| Recovery Tracker | Prior-month recovery stats + current-month dispute queue |

### Across all pages

- **Period selector** — any month/year in sidebar (replaces hardcoded dates)
- **Excel export** — 3-sheet workbook: Summary KPIs · Exception Report · Dispute Queue
- **CSV export** — raw exception data
- **Email digest** — sends exception summary + Excel attachment via SMTP
- **Demo data** — all 4 verticals generate realistic SA data out of the box
- **CSV upload** — switch to Upload mode in sidebar for real client data

---

## Active Verticals

| Vertical | Counterparty | Primary Entity | Exception Types |
|----------|-------------|----------------|-----------------|
| Insurance Broker | Insurer | Policy | RATE_MISMATCH, MISSING_PAYMENT, PARTIAL_PAYMENT |
| Accounting Firm | Client | Invoice | UNDERPAYMENT, OVERPAYMENT, MISSING |
| Construction | Contractor | Project | COST_OVERRUN, RETENTION_DISPUTE |
| Logistics | Vehicle/Driver | Trip | FUEL_VARIANCE, ROUTE_DEVIATION |

---

## Email Digest Setup

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Fill in your Gmail App Password (not your login password — generate at myaccount.google.com → Security → App passwords)
3. Restart Streamlit — the "Send Digest" button in the sidebar now works

The `secrets.toml` file is gitignored and never committed.

---

## Tests

```bash
pytest tests/ -v
```

6 test files, full coverage per vertical (schema validation, demo data, KPI calculation, reconciliation logic).

---

## Revenue Model

| Item | Price |
|------|-------|
| Setup / onboarding | R5,000 once-off |
| Monthly retainer | R1,500/month |

**Path to R100k/month:** 67 active clients × R1,500

---

## Status (June 16 2026)

| Area | Status | Notes |
|------|--------|-------|
| 4 verticals | ✅ Done | Insurance Broker, Accounting, Construction, Logistics |
| Period selector | ✅ Done | Any month/year |
| Excel export | ✅ Done | 3-sheet workbook on all pages |
| Email digest | ✅ Done | SMTP + Excel attachment |
| Demo data | ✅ Done | All 4 verticals |
| CSV upload | ✅ Done | Upload mode in sidebar |
| Tests | ✅ Good | 6 test files |
| SMTP secrets | ⚠️ Config needed | Create .streamlit/secrets.toml from example |
| Auth | ✅ Done | Single shared password gate via `st.secrets["dashboard_password"]` in `app.py` — not full multi-tenant access control |
| Streamlit Cloud deploy | ✅ Shim added | `streamlit_app.py` exists pointing to `app.py` — actual Streamlit Cloud deployment/push still to be done by the owner |

---

## What's Next

1. Create `.streamlit/secrets.toml` with Gmail App Password and a `dashboard_password`
2. Push to Streamlit Cloud and confirm the `streamlit_app.py` entry point deploys cleanly
3. Book Insurance Broker demo call
