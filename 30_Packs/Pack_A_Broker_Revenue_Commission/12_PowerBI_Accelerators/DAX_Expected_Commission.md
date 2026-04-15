# DAX — Expected Commission Model Measures

Assumptions:
- Fact_Commission has [CommissionAmount]
- Fact_ExpectedCommission has [ExpectedCommissionAmount]
- Both relate to Dim_Date and Dim_Policy (or PolicyNumber dimension)

Measures:
- Actual Commission := SUM ( Fact_Commission[CommissionAmount] )
- Expected Commission := SUM ( Fact_ExpectedCommission[ExpectedCommissionAmount] )
- Leakage (R) := [Expected Commission] - [Actual Commission]
- Leakage % := DIVIDE ( [Leakage (R)], [Expected Commission] )

Quality:
- Expected Coverage % :=
VAR totalPolicies = DISTINCTCOUNT ( Dim_Policy[PolicyNumber] )
VAR modelPolicies = CALCULATE ( DISTINCTCOUNT ( Fact_ExpectedCommission[PolicyNumber] ) )
RETURN DIVIDE ( modelPolicies, totalPolicies )

- Missing Ongoing (Count) :=
CALCULATE (
    DISTINCTCOUNT ( Dim_Policy[PolicyNumber] ),
    Fact_ExpectedCommission[ExpectedCommissionAmount] > 0,
    [Actual Commission] = 0
)
