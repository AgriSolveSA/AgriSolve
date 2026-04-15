# Pack A Quick Start (Demo → Client)

## Demo build (fast)
1) Use the sample exports in:
   /30_Packs/Pack_A_Broker_Revenue_Commission/13_Client_Export_Standards/...
2) Load into Power BI using Power Query:
   - Normalize dirty CSV into the clean schema
3) Build pages from wireframes:
   - Executive, Provider/Adviser, Reconciliation, Exceptions, Drilldown
4) Add measures from:
   /30_Packs/Pack_A_Broker_Revenue_Commission/12_PowerBI_Accelerators/DAX_Expected_Commission.md

## Client build (repeatable)
1) Get 1 month of commission export + adviser/provider lists
2) Validate mapping completeness:
   - % lines with policy number
   - % lines with adviser
3) Deliver Pack A base
4) Only then propose Expected Model upgrade (needs premium/policy)
