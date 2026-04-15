// Pseudocode: Break-Even Calculator (Template)

DEFINE Inputs:
    - MonthlySalaryTarget (after tax) = R______
    - MonthlyBusinessOverhead (software, phone, travel) = R______
    - BufferContributionPerMonth = R______

DEFINE RevenuePerClient:
    Tier1:
        - SetupFee = R______
        - MonthlyFee = R______
    Tier2:
        - SetupFee = R______
        - MonthlyFee = R______
    Tier3:
        - OnceOffFee = R______

DEFINE Formulas:
    MonthlyTarget = MonthlySalaryTarget + MonthlyBusinessOverhead + BufferContributionPerMonth

    RecurringClientsNeeded = MonthlyTarget / AverageMonthlyFee

    ExpectedMonthlyRevenue = (NewClientsPerMonth * AvgSetupFee) + (TotalRetainedClients * AvgMonthlyFee)

DEFINE RulesOfThumb:
    - Early months = setup-heavy (cash spikes)
    - Long-term freedom = recurring base + cash buffer

DEFINE DecisionGate:
    Condition1: RecurringRevenue >= ThresholdPercentOfMonthlyTarget
    Condition2: BusinessCashBuffer >= 2–3 months household burn
    IF Condition1 AND Condition2:
        - Approve unpaid leave
    ELSE:
        - Defer leave planning
