// Pseudocode: Expected Commission Model (DAX Measures)

DEFINE Measures:
    ActualCommission =
        SUM ( Fact_Commission[CommissionAmount] )

    ExpectedCommission =
        SUM ( Fact_ExpectedCommission[ExpectedCommissionAmount] )

    Leakage_R =
        [ExpectedCommission] - [ActualCommission]

    LeakagePercent =
        DIVIDE ( [Leakage_R], [ExpectedCommission] )

DEFINE QualityChecks:
    ExpectedCoveragePercent =
        VAR totalPolicies = DISTINCTCOUNT ( Dim_Policy[PolicyNumber] )
        VAR modelPolicies = CALCULATE (
            DISTINCTCOUNT ( Fact_ExpectedCommission[PolicyNumber] )
        )
        RETURN DIVIDE ( modelPolicies, totalPolicies )

    MissingOngoing_Count =
        CALCULATE (
            DISTINCTCOUNT ( Dim_Policy[PolicyNumber] ),
            Fact_ExpectedCommission[ExpectedCommissionAmount] > 0,
            [ActualCommission] = 0
        )
