// Pseudocode: Client Export Standards Pack

DEFINE Purpose:
    - Reduce refresh failures
    - Standardize client data delivery

DEFINE Components:
    Component1: FileNamingConventions
        - GL = "GL_YYYYMM.xlsx"
        - AR = "AR_YYYYMM.csv"
        - Sales = "Sales_YYYYMM.csv"
        - Masters = {Customers.xlsx, Products.xlsx}

    Component2: FolderStructureConventions
        Root = /Exports
            SubFolder1 = /GL
            SubFolder2 = /AR
            SubFolder3 = /Sales
            SubFolder4 = /Masters

    Component3: SampleExports
        - CleanExport = Example with correct headers, ISO dates, decimals
        - DirtyExport = Example with broken headers, blank rows, wrong formats

    Component4: SchemaChangeChecklist
        - Notify Vantix before changing exports
        - Document header changes
        - Validate column types
        - Confirm folder + naming compliance

DEFINE ComplianceRule:
    IF ClientCannotComply:
        - Assign to Tier3 (Buy-Out)
        OR
        - Quote DataEngineering separately
