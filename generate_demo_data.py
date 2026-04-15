"""
Generate realistic demo data for the Commission Reconciliation Dashboard.
Produces a policy register + 3 insurer commission statements with 8 seeded discrepancies.

Run once:  python generate_demo_data.py
"""

import pandas as pd
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

# ── Output ──────────────────────────────────────────────────────────────────
DATA_DIR = Path("data/demo")
DATA_DIR.mkdir(parents=True, exist_ok=True)

STATEMENT_MONTH = "2026-03-31"

# ── Reference data ───────────────────────────────────────────────────────────
INSURERS = {
    "Pinnacle Life Insurance": {
        "products": ["Life Cover", "Disability", "Critical Illness"],
        "rates":    [0.025,        0.020,        0.025],
        "prefix":   "PIL",
    },
    "Meridian Short-Term": {
        "products": ["Motor",  "Household Contents", "Building"],
        "rates":    [0.125,    0.150,                0.125],
        "prefix":   "MST",
    },
    "Apex Financial Services": {
        "products": ["Income Protection", "Life Cover", "Group Life"],
        "rates":    [0.020,               0.025,        0.015],
        "prefix":   "AFS",
    },
}

PREMIUM_RANGES = {
    "Life Cover":           (1500, 8000),
    "Disability":           (1200, 5000),
    "Critical Illness":     (800,  3500),
    "Motor":                (1200, 4500),
    "Household Contents":   (500,  2000),
    "Building":             (800,  3500),
    "Income Protection":    (1500, 6000),
    "Group Life":           (3000, 12000),
}

SURNAMES = [
    "Dlamini","Nkosi","Smith","Van der Berg","Patel","Botha","Khumalo",
    "Meyer","Ndlovu","Joubert","Mokoena","Williams","Pretorius","Sithole",
    "Steyn","Mahlangu","De Villiers","Zulu","Venter","Naidoo",
]
INITIALS = [f"{a}{b}" for a in "ABCDEFGHIJKLM" for b in "ABCDEFGHIJKLM"]

# Weighted toward Active (realistic book distribution)
STATUS_POOL = ["Active"] * 82 + ["Lapsed"] * 12 + ["Cancelled"] * 6

# ── Seeded discrepancies ─────────────────────────────────────────────────────
# These override generated data for specific policy numbers.
# 8 exceptions totalling ~R16 500 in disputes.
OVERRIDES = {
    # POL-1024: Lapsed in register — insurer still paid commission (R3 200)
    "POL-1024": {
        "register": {"policy_status": "Lapsed", "expected_monthly_commission": 0.0},
        "statement": {"commission_amount": 3200.00, "commission_rate": 0.025,
                      "monthly_premium": 4800, "include": True},
    },
    # POL-1047: Rate mismatch — insurer paid at 2.0% instead of agreed 2.5%
    "POL-1047": {
        "register": {"agreed_commission_rate": 0.025, "monthly_premium": 7250,
                     "expected_monthly_commission": 181.25},
        "statement": {"commission_amount": 145.00, "commission_rate": 0.020,
                      "monthly_premium": 7250, "include": True},
    },
    # POL-1065: Partial payment — insurer short-paid without explanation
    "POL-1065": {
        "register": {"expected_monthly_commission": 4500.00, "monthly_premium": 6000,
                     "agreed_commission_rate": 0.125},
        "statement": {"commission_amount": 2250.00, "commission_rate": 0.125,
                      "monthly_premium": 6000, "include": True},
    },
    # POL-2018: Active policy — completely omitted from insurer statement
    "POL-2018": {
        "register": {"policy_status": "Active", "monthly_premium": 3200,
                     "agreed_commission_rate": 0.125,
                     "expected_monthly_commission": 400.00},
        "statement": {"include": False},
    },
    # POL-2039: Wrong premium basis — commission rate correct, premium input wrong
    "POL-2039": {
        "register": {"policy_status": "Active", "monthly_premium": 4200,
                     "agreed_commission_rate": 0.150,
                     "expected_monthly_commission": 630.00},
        "statement": {"commission_amount": 420.00, "commission_rate": 0.150,
                      "monthly_premium": 2800, "include": True},
    },
    # POL-3012: Rate mismatch — income protection paid at 1.0% instead of 2.0%
    "POL-3012": {
        "register": {"policy_status": "Active", "agreed_commission_rate": 0.020,
                     "monthly_premium": 5800,
                     "expected_monthly_commission": 116.00},
        "statement": {"commission_amount": 58.00, "commission_rate": 0.010,
                      "monthly_premium": 5800, "include": True},
    },
    # POL-3051: Cancelled policy — insurer paid R4 100 claw-back incorrectly
    "POL-3051": {
        "register": {"policy_status": "Cancelled", "expected_monthly_commission": 0.0},
        "statement": {"commission_amount": 4100.00, "commission_rate": 0.025,
                      "monthly_premium": 5500, "include": True},
    },
}

# Ghost policy: in statement but not in register at all
GHOST_ENTRY = {
    "insurer_name":    "Meridian Short-Term",
    "policy_number":   "POL-GHOST-001",
    "insurer_ref":     "MST999001",
    "client_surname":  "Unknown",
    "client_initials": "XX",
    "product_type":    "Motor",
    "commission_type": "Renewal",
    "monthly_premium": 2600,
    "commission_rate": 0.125,
    "commission_amount": 325.00,
    "statement_date":  STATEMENT_MONTH,
}


# ── Generators ───────────────────────────────────────────────────────────────

def _rand_premium(product: str) -> int:
    lo, hi = PREMIUM_RANGES.get(product, (500, 5000))
    return random.randint(lo // 100, hi // 100) * 100  # round to nearest 100


def build_register() -> pd.DataFrame:
    rows = []
    for ins_idx, (insurer, cfg) in enumerate(INSURERS.items()):
        for i in range(80):
            pol_num = f"POL-{(ins_idx + 1) * 1000 + i + 1:04d}"
            product = random.choices(cfg["products"])[0]
            rate = cfg["rates"][cfg["products"].index(product)]
            premium = _rand_premium(product)
            status = random.choice(STATUS_POOL)
            inception = date(2020, 1, 1) + timedelta(days=random.randint(0, 1460))
            expected = round(premium * rate, 2) if status == "Active" else 0.0

            row = {
                "policy_number":              pol_num,
                "insurer_name":               insurer,
                "insurer_ref":                f"{cfg['prefix']}{(ins_idx + 1) * 1000 + i + 1:06d}",
                "client_surname":             random.choice(SURNAMES),
                "client_initials":            random.choice(INITIALS),
                "product_type":               product,
                "policy_status":              status,
                "inception_date":             inception.strftime("%Y-%m-%d"),
                "agreed_commission_rate":     rate,
                "monthly_premium":            premium,
                "expected_monthly_commission": expected,
            }

            # Apply register-side overrides
            if pol_num in OVERRIDES:
                row.update(OVERRIDES[pol_num].get("register", {}))

            rows.append(row)
    return pd.DataFrame(rows)


def build_statements(register: pd.DataFrame) -> dict[str, pd.DataFrame]:
    statements: dict[str, list] = {ins: [] for ins in INSURERS}

    for _, row in register.iterrows():
        pol_num = row["policy_number"]
        insurer = row["insurer_name"]
        override = OVERRIDES.get(pol_num, {}).get("statement", {})

        # Skip if overridden to exclude
        if override.get("include") is False:
            continue

        # Only pay Active policies by default
        if row["policy_status"] != "Active" and pol_num not in OVERRIDES:
            continue

        if row["expected_monthly_commission"] == 0 and pol_num not in OVERRIDES:
            continue

        entry = {
            "statement_date":   STATEMENT_MONTH,
            "insurer_name":     insurer,
            "policy_number":    pol_num,
            "insurer_ref":      row["insurer_ref"],
            "client_surname":   row["client_surname"],
            "client_initials":  row["client_initials"],
            "product_type":     row["product_type"],
            "commission_type":  "Renewal",
            "monthly_premium":  override.get("monthly_premium", row["monthly_premium"]),
            "commission_rate":  override.get("commission_rate", row["agreed_commission_rate"]),
            "commission_amount": override.get(
                "commission_amount", row["expected_monthly_commission"]
            ),
        }
        statements[insurer].append(entry)

    # Add the ghost entry
    statements["Meridian Short-Term"].append(GHOST_ENTRY)

    return {ins: pd.DataFrame(rows) for ins, rows in statements.items()}


def generate_demo() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Return (register_df, {insurer: statement_df}) — used by app.py directly."""
    register = build_register()
    statements = build_statements(register)
    return register, statements


def save_demo() -> None:
    """Write CSVs to data/demo/."""
    register, statements = generate_demo()

    register_path = DATA_DIR / "policy_register.csv"
    register.to_csv(register_path, index=False)
    print(f"  Saved: {register_path}  ({len(register)} policies)")

    for insurer, df in statements.items():
        slug = insurer.lower().replace(" ", "_")
        path = DATA_DIR / f"commission_{slug}_2026_03.csv"
        df.to_csv(path, index=False)
        print(f"  Saved: {path}  ({len(df)} entries)")

    print(f"\nDemo data ready in {DATA_DIR}/")
    print(f"  Total policies in register : {len(register)}")
    total_stmt = sum(len(df) for df in statements.values())
    print(f"  Total statement lines      : {total_stmt}")
    print(f"  Seeded discrepancies       : {len(OVERRIDES) + 1}  (incl. ghost)")


if __name__ == "__main__":
    save_demo()
