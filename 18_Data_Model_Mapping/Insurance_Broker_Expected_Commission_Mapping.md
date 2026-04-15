# Mapping — Expected Commission (Fact_ExpectedCommission)

Minimum columns:
- Period (YYYYMM)
- PolicyNumber
- Provider
- Adviser
- CommissionType (Initial/Ongoing/Fee/Override)
- ExpectedCommissionAmount
- RuleId (optional; traceability)

Relationships:
- PolicyNumber -> Dim_Policy (or PolicyNumber dimension)
- Period -> Dim_Date
- Provider/Adviser -> their dims (optional)

Design principle:
Expected and Actual should share the same grain so variance is meaningful.
