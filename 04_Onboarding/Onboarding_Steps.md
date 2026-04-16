// Pseudocode: Data Processing Workflow (AgriSolve SME Dashboard)

DEFINE WorkflowSteps:

    STEP ReceiveData:
        - Input = RequiredDataSources (Financial exports, Customer list, Product list)
        - Validate file naming conventions
        - Confirm schema compatibility

    STEP Validate:
        - Check data completeness
        - Verify column formats
        - Ensure mapping aligns with CoreTables (Fact_Financials, Fact_Operations, Fact_AR, Dim_Date)

    STEP Load:
        - Ingest validated data into staging area
        - Apply standardized schema transformations
        - Populate fact + dimension tables

    STEP Publish:
        - Deploy Power BI dataset
        - Apply dashboard templates (Executive, Financials, Ops, Cash, Exceptions, Details)
        - Enforce visual design constraints (<= 6 visuals per page, neutral colors)

    STEP Refresh:
        - Schedule automated dataset refresh
        - Monitor refresh status
        - Trigger alerts on failure or drift
