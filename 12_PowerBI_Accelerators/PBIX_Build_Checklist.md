// Pseudocode: PBIX Build Checklist (Sequential Order)

STEP 1: CreateDimDate
    - Build complete calendar table
    - Mark as DateTable

STEP 2: CreateDimAccount
    - Mapping table for Revenue/Cost/etc.

STEP 3: LoadFactFinancials
    - Source = Trial Balance / GL export

STEP 4: LoadFactAR
    - Source = Debtors ageing export

STEP 5: CreateRelationships
    - Star schema design

STEP 6: CreateMeasures
    - Use DAX Measures Library

STEP 7: BuildPages
    - Layout = Wireframe PNGs

STEP 8: PublishToClientWorkspace

STEP 9: ConfigureRefreshAndGateway
    - Client-owned gateway
    - Schedule refresh

STEP 10: TestRefresh
    - Run scheduled refresh for 7 days
    - PassCondition = Stable with no manual intervention
