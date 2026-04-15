# Insurance Broker — Revenue & Commission Pack KPIs (v6.2)

## Purpose
This pack answers the broker's #1 question:
**"Are we losing commission / revenue — and where?"**

It stays firmly in **operations + financial visibility** (not advice).

---

## Entities (Core Dimensions)
- Adviser (rep / broker)
- Client
- Policy (policy number / contract)
- Product / Provider / Insurer
- Period (month, quarter, YTD)

---

## Fact Tables (Minimum Viable)
### Fact_Commission
Columns (minimum):
- Period (YYYYMM)
- PolicyNumber
- Provider
- Adviser
- Client (optional)
- CommissionType (Initial / Ongoing / Fee / Override)
- CommissionAmount
- ExpectedCommissionAmount (optional but powerful)
- StatementId / SourceFile (traceability)

### Fact_Policies (optional but recommended)
- PolicyNumber
- Status (Active / Lapsed / Cancelled / Pending)
- StartDate
- EndDate (if any)
- Premium (if available)
- ProductType
- Adviser
- Provider
- Client

---

## Executive KPIs (Page 1)
1) **Total Commission (Month / YTD)** = SUM(CommissionAmount)
2) **Ongoing Commission** = SUM where CommissionType = Ongoing
3) **Initial Commission** = SUM where CommissionType = Initial
4) **Commission per Adviser** = Total Commission by Adviser
5) **Commission Leakage (Expected vs Actual)** (if expected exists) = Expected - Actual (+ %)
6) **Top Variances (Rands)** by Provider / Adviser / Policy

---

## Trend & Concentration KPIs (Page 2)
- Commission MoM change (value and %)
- Rolling 3-month average commission
- Provider concentration (Top 1 / Top 3 share)
- Adviser concentration (Top 1 / Top 3 share)

---

## Reconciliation KPIs (Page 3)
- **Matched Policies %** (statement lines that match known policies)
- **Unmatched Statement Lines** (count + value)
- **Missing Policies** (policies active but no commission received in period)
- **Duplicate Statement Lines** (count + value)
- **Negative / Reversal Lines** (count + value)

---

## Retention / Lapse Signals (Page 4)
(Uses Fact_Policies if available, otherwise infer from commission drops)
- Policies Lapsed (count)
- Commission lost due to lapses (value/estimate)
- Retention rate (Active end / Active start)
- Adviser lapse rate comparison

---

## Exceptions (Page 5)
Flag as exceptions for review:
- Commission drop > X% MoM per adviser
- Provider variance > X% vs rolling avg
- Policies with 2+ months of missing ongoing commission
- Statement lines with missing policy number / adviser
- Duplicates above threshold
- Reversals above threshold

---

## Drilldowns (Page 6)
- Commission statement lines (traceable to source)
- Policy list with last commission date
- Adviser performance table
- Provider performance table

---

## Standard Exclusions (keep you safe)
- No product recommendations
- No “advice” outputs
- No compliance determinations
- No customer suitability scoring
- No underwriting / pricing analytics (unless separately quoted)
