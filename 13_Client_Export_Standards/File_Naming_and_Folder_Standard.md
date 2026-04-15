// Pseudocode: File Naming + Folder Standard (Client-Hosted)

DEFINE FolderStructure:
    Root = /Exports
        SubFolder1 = /GL
        SubFolder2 = /AR
        SubFolder3 = /Sales
        SubFolder4 = /Masters

DEFINE FileNamingConventions:
    GL = "GL_YYYYMM.xlsx"
    AR = "AR_YYYYMM.csv"
    Sales = "Sales_YYYYMM.csv"
    Masters:
        - Customers.xlsx
        - Products.xlsx

DEFINE Rules:
    Rule1: ColumnHeaders must not change without notifying Vantix
        - Use SchemaChangeChecklist if changes required
    Rule2: No blank rows above headers
    Rule3: Use ISO dates (YYYY-MM-DD) where possible
    Rule4: Use '.' for decimals
    Rule5: No thousands separators

DEFINE NonComplianceHandling:
    IF ClientCannotComply:
        - Assign to Tier3 (Buy-Out)
        OR
        - Quote DataEngineering separately
