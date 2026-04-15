// Pseudocode: DAX Measures Library (Starter Set)

DEFINE TimeIntelligence:
    TotalAmount = SUM ( Fact_Financials[Amount] )
    TotalAmount_MTD = TOTALMTD ( [TotalAmount], Dim_Date[Date] )
    TotalAmount_YTD = TOTALYTD ( [TotalAmount], Dim_Date[Date] )
    TotalAmount_PY = CALCULATE ( [TotalAmount], SAMEPERIODLASTYEAR ( Dim_Date[Date] ) )
    YoYPercent = DIVIDE ( [TotalAmount] - [TotalAmount_PY], [TotalAmount_PY] )

DEFINE RevenueCostMargin:
    Revenue = CALCULATE ( [TotalAmount], Dim_Account[Type] = "Revenue" )
    Cost = CALCULATE ( [TotalAmount], Dim_Account[Type] = "Cost" )
    GrossMargin = [Revenue] - [Cost]
    GrossMarginPercent = DIVIDE ( [GrossMargin], [Revenue] )

DEFINE Trends:
    MoMChange = [TotalAmount] - CALCULATE ( [TotalAmount], DATEADD ( Dim_Date[Date], -1, MONTH ) )
    MoMPercent = DIVIDE ( [MoMChange], CALCULATE ( [TotalAmount], DATEADD ( Dim_Date[Date], -1, MONTH ) ) )

DEFINE Debtors_AR:
    ARBalance = SUM ( Fact_AR[Balance] )
    AROverdue = CALCULATE ( [ARBalance], Fact_AR[AgeBucket] IN { "60+", "90+", "120+" } )
    AROverduePercent = DIVIDE ( [AROverdue], [ARBalance] )

DEFINE Exceptions:
    ExceptionFlag_MarginDrop =
        VAR curr = [GrossMarginPercent]
        VAR prev = CALCULATE ( [GrossMarginPercent], DATEADD ( Dim_Date[Date], -1, MONTH ) )
        RETURN IF ( NOT ISBLANK(prev) && curr < prev * 0.9, 1, 0 )
