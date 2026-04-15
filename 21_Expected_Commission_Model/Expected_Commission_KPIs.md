# Expected Commission KPIs

## Core
- Actual Commission = SUM(Fact_Commission[CommissionAmount])
- Expected Commission = SUM(Fact_ExpectedCommission[ExpectedCommissionAmount])
- Leakage (R) = Expected - Actual
- Leakage % = (Expected - Actual) / Expected

## Coverage / Confidence
- % Policies with Expected Model = Policies where expected rule matched / total policies
- % Statement Lines Matched to Policy = matched / total statement lines

## Exceptions
- High Leakage Policies (top N by Rand)
- Provider Leakage (by provider)
- Adviser Leakage (by adviser)
- Missing Ongoing Commission (expected ongoing > 0, actual = 0)

## Boundaries
This is not a compliance or advice tool; it is revenue/commission reconciliation visibility.
