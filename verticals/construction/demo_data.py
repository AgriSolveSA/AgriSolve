"""
Construction vertical demo data.
Single job: generate deterministic projects register and contractor cost-line DataFrames.

Seeded exceptions (6 total):
  COST_OVERRUN  (High)   — PRJ-NC-002, PRJ-VW-002 (actual > budgeted * 1.1)
  SLOW_PAYMENT  (High)   — PRJ-VW-001, PRJ-BC-001 (outstanding > 45 days)
  MARGIN_EROSION (Medium) — PRJ-VW-003, PRJ-BC-002 (margin < 10 % of contract value)

Total projects     : 7 (2 Ndlovu + 3 Veld&Weg + 2 Boplaas)
Total contractors  : 3
Total cost lines   : 39
Total at risk      : R 428,000
"""

import pandas as pd

_NC = "Ndlovu Construction"
_VW = "Veld & Weg Builders"
_BC = "Boplaas Civils"


def _build_projects() -> pd.DataFrame:
    rows = [
        # PRJ-NC-001: Grain Silo Extension — clean
        {
            "project_number":   "PRJ-NC-001",
            "project_name":     "Grain Silo Extension",
            "contractor_name":  _NC,
            "start_date":       "2025-01-01",
            "end_date":         "2025-04-30",
            "contract_value":   350_000.0,
            "budgeted_cost":    280_000.0,
            "actual_cost":      270_000.0,
            "billed_amount":    350_000.0,
            "payment_received": 350_000.0,
            "days_outstanding": 0,
            "payment_status":   "Paid",
        },
        # PRJ-NC-002: Irrigation Pipeline — COST_OVERRUN (145k > 120k * 1.1 = 132k)
        {
            "project_number":   "PRJ-NC-002",
            "project_name":     "Irrigation Pipeline",
            "contractor_name":  _NC,
            "start_date":       "2025-05-01",
            "end_date":         "2025-08-31",
            "contract_value":   180_000.0,
            "budgeted_cost":    120_000.0,
            "actual_cost":      145_000.0,
            "billed_amount":    180_000.0,
            "payment_received": 180_000.0,
            "days_outstanding": 0,
            "payment_status":   "Paid",
        },
        # PRJ-VW-001: Access Road Phase 1 — SLOW_PAYMENT (days=55 > 45, Partial)
        {
            "project_number":   "PRJ-VW-001",
            "project_name":     "Access Road Phase 1",
            "contractor_name":  _VW,
            "start_date":       "2025-02-01",
            "end_date":         "2025-05-31",
            "contract_value":   520_000.0,
            "budgeted_cost":    420_000.0,
            "actual_cost":      415_000.0,
            "billed_amount":    520_000.0,
            "payment_received": 350_000.0,
            "days_outstanding": 55,
            "payment_status":   "Partial",
        },
        # PRJ-VW-002: Pack House Roof — COST_OVERRUN (90.5k > 80k * 1.1 = 88k)
        {
            "project_number":   "PRJ-VW-002",
            "project_name":     "Pack House Roof Replacement",
            "contractor_name":  _VW,
            "start_date":       "2025-03-01",
            "end_date":         "2025-06-30",
            "contract_value":   95_000.0,
            "budgeted_cost":    80_000.0,
            "actual_cost":      90_500.0,
            "billed_amount":    95_000.0,
            "payment_received": 95_000.0,
            "days_outstanding": 0,
            "payment_status":   "Paid",
        },
        # PRJ-VW-003: Barn Renovation — MARGIN_EROSION (margin 8.3 % < 10 %)
        {
            "project_number":   "PRJ-VW-003",
            "project_name":     "Barn Renovation",
            "contractor_name":  _VW,
            "start_date":       "2025-06-01",
            "end_date":         "2025-09-30",
            "contract_value":   145_000.0,
            "budgeted_cost":    140_000.0,
            "actual_cost":      133_000.0,
            "billed_amount":    145_000.0,
            "payment_received": 145_000.0,
            "days_outstanding": 0,
            "payment_status":   "Paid",
        },
        # PRJ-BC-001: Pump Station Rebuild — SLOW_PAYMENT (days=65 > 45, Overdue)
        {
            "project_number":   "PRJ-BC-001",
            "project_name":     "Pump Station Rebuild",
            "contractor_name":  _BC,
            "start_date":       "2025-03-01",
            "end_date":         "2025-06-30",
            "contract_value":   210_000.0,
            "budgeted_cost":    170_000.0,
            "actual_cost":      168_000.0,
            "billed_amount":    210_000.0,
            "payment_received": 0.0,
            "days_outstanding": 65,
            "payment_status":   "Overdue",
        },
        # PRJ-BC-002: Farm Worker Housing — MARGIN_EROSION (margin 7.4 % < 10 %)
        {
            "project_number":   "PRJ-BC-002",
            "project_name":     "Farm Worker Housing",
            "contractor_name":  _BC,
            "start_date":       "2025-07-01",
            "end_date":         "2025-11-30",
            "contract_value":   380_000.0,
            "budgeted_cost":    340_000.0,
            "actual_cost":      352_000.0,
            "billed_amount":    380_000.0,
            "payment_received": 380_000.0,
            "days_outstanding": 0,
            "payment_status":   "Paid",
        },
    ]
    return pd.DataFrame(rows)


def _build_cost_lines() -> dict[str, pd.DataFrame]:
    """Return {contractor_name: cost_lines_df} — 39 lines across 7 projects."""

    def line(proj, contractor, category, description, budgeted, actual, date):
        return {
            "project_number":  proj,
            "contractor_name": contractor,
            "cost_category":   category,
            "description":     description,
            "budgeted_amount": budgeted,
            "actual_amount":   actual,
            "invoice_date":    date,
        }

    nc: list[dict] = []
    vw: list[dict] = []
    bc: list[dict] = []

    # ── PRJ-NC-001: Grain Silo Extension (budget=280k, actual=270k) ──────────
    nc += [
        line("PRJ-NC-001", _NC, "Labour",           "Site labour",       120_000.0, 115_000.0, "2025-03-01"),
        line("PRJ-NC-001", _NC, "Materials",         "Concrete & steel",   90_000.0,  88_000.0, "2025-02-01"),
        line("PRJ-NC-001", _NC, "Plant & Equipment", "Crane hire",          40_000.0,  38_000.0, "2025-02-15"),
        line("PRJ-NC-001", _NC, "Subcontractors",    "Electrical works",    20_000.0,  19_000.0, "2025-03-15"),
        line("PRJ-NC-001", _NC, "Admin",             "Site admin",           5_000.0,   5_000.0, "2025-03-30"),
        line("PRJ-NC-001", _NC, "Survey",            "Land survey",          5_000.0,   5_000.0, "2025-01-15"),
    ]

    # ── PRJ-NC-002: Irrigation Pipeline (budget=120k, actual=145k) ───────────
    nc += [
        line("PRJ-NC-002", _NC, "Labour",           "Pipe laying crew",    50_000.0,  62_000.0, "2025-07-01"),
        line("PRJ-NC-002", _NC, "Materials",         "PVC pipes & fittings", 35_000.0, 42_000.0, "2025-06-15"),
        line("PRJ-NC-002", _NC, "Plant & Equipment", "Excavator hire",       20_000.0,  25_000.0, "2025-06-01"),
        line("PRJ-NC-002", _NC, "Subcontractors",    "Pump installation",    10_000.0,  12_000.0, "2025-07-15"),
        line("PRJ-NC-002", _NC, "Admin",             "Site admin",            3_000.0,   3_000.0, "2025-07-30"),
        line("PRJ-NC-002", _NC, "Survey",            "Route survey",          2_000.0,   1_000.0, "2025-05-15"),
    ]

    # ── PRJ-VW-001: Access Road Phase 1 (budget=420k, actual=415k) ───────────
    vw += [
        line("PRJ-VW-001", _VW, "Labour",           "Road grading crew",  170_000.0, 168_000.0, "2025-04-01"),
        line("PRJ-VW-001", _VW, "Materials",         "Gravel & bitumen",   120_000.0, 118_000.0, "2025-03-15"),
        line("PRJ-VW-001", _VW, "Plant & Equipment", "Grader & roller",     85_000.0,  84_000.0, "2025-03-01"),
        line("PRJ-VW-001", _VW, "Subcontractors",    "Drainage works",       30_000.0,  30_000.0, "2025-04-15"),
        line("PRJ-VW-001", _VW, "Admin",             "Site admin",           10_000.0,  10_000.0, "2025-04-30"),
        line("PRJ-VW-001", _VW, "Survey",            "Road survey",           5_000.0,   5_000.0, "2025-02-15"),
    ]

    # ── PRJ-VW-002: Pack House Roof (budget=80k, actual=90.5k) ───────────────
    vw += [
        line("PRJ-VW-002", _VW, "Labour",           "Roofing team",        35_000.0,  40_000.0, "2025-05-01"),
        line("PRJ-VW-002", _VW, "Materials",         "Steel & sheeting",    25_000.0,  29_000.0, "2025-04-15"),
        line("PRJ-VW-002", _VW, "Plant & Equipment", "Scaffold hire",        12_000.0,  14_000.0, "2025-04-01"),
        line("PRJ-VW-002", _VW, "Subcontractors",    "Gutter installation",   6_000.0,   6_500.0, "2025-05-15"),
        line("PRJ-VW-002", _VW, "Admin",             "Site admin",            2_000.0,   1_000.0, "2025-05-30"),
    ]

    # ── PRJ-VW-003: Barn Renovation (budget=140k, actual=133k) ───────────────
    vw += [
        line("PRJ-VW-003", _VW, "Labour",           "Renovation crew",     60_000.0,  57_000.0, "2025-08-01"),
        line("PRJ-VW-003", _VW, "Materials",         "Timber & roofing",    42_000.0,  40_000.0, "2025-07-15"),
        line("PRJ-VW-003", _VW, "Plant & Equipment", "Equipment hire",       25_000.0,  24_000.0, "2025-07-01"),
        line("PRJ-VW-003", _VW, "Subcontractors",    "Electrical upgrade",   10_000.0,   9_000.0, "2025-08-15"),
        line("PRJ-VW-003", _VW, "Admin",             "Site admin",            3_000.0,   3_000.0, "2025-08-30"),
    ]

    # ── PRJ-BC-001: Pump Station Rebuild (budget=170k, actual=168k) ──────────
    bc += [
        line("PRJ-BC-001", _BC, "Labour",           "Civil crew",          68_000.0,  67_000.0, "2025-05-01"),
        line("PRJ-BC-001", _BC, "Materials",         "Concrete & pipework", 52_000.0,  51_000.0, "2025-04-15"),
        line("PRJ-BC-001", _BC, "Plant & Equipment", "Crane hire",           28_000.0,  28_000.0, "2025-04-01"),
        line("PRJ-BC-001", _BC, "Subcontractors",    "Mechanical works",     15_000.0,  15_000.0, "2025-05-15"),
        line("PRJ-BC-001", _BC, "Admin",             "Site admin",            4_000.0,   4_000.0, "2025-05-30"),
        line("PRJ-BC-001", _BC, "Survey",            "Site survey",           3_000.0,   3_000.0, "2025-03-15"),
    ]

    # ── PRJ-BC-002: Farm Worker Housing (budget=340k, actual=352k) ───────────
    bc += [
        line("PRJ-BC-002", _BC, "Labour",           "Construction crew",  140_000.0, 147_000.0, "2025-09-01"),
        line("PRJ-BC-002", _BC, "Materials",         "Bricks & cement",   105_000.0, 109_000.0, "2025-08-15"),
        line("PRJ-BC-002", _BC, "Plant & Equipment", "Mixer & scaffold",    55_000.0,  57_000.0, "2025-08-01"),
        line("PRJ-BC-002", _BC, "Subcontractors",    "Plumbing & electrical", 32_000.0, 32_000.0, "2025-09-15"),
        line("PRJ-BC-002", _BC, "Admin",             "Site admin",            8_000.0,   7_000.0, "2025-09-30"),
    ]

    return {
        _NC: pd.DataFrame(nc),
        _VW: pd.DataFrame(vw),
        _BC: pd.DataFrame(bc),
    }


def generate_demo() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Return (projects_df, {contractor_name: cost_lines_df})."""
    return _build_projects(), _build_cost_lines()
