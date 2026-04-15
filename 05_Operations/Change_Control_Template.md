// Pseudocode: Change Control Template (Scope Protection)

DEFINE ChangeControl:

    INPUTS:
        ClientName
        RequestDate
        ChangeDescription

    CLASSIFICATION:
        OPTION BugFix:
            - Included in scope
        OPTION SmallChangeWithinTier:
            - Included in scope
        OPTION NewPageOrMajorVisualChange:
            - Requires separate quote
        OPTION NewDataSourceOrSchemaChange:
            - Requires separate quote
        OPTION NewEntityOrMultiCompanyConsolidation:
            - Requires separate quote

    IMPACT:
        - EstimatedHours
        - Risks
        - Dependencies

    COMMERCIAL:
        - Status = Included OR NotIncluded
        - QuoteAmount (if applicable)
        - ETA (must be agreed in writing)

    APPROVALS:
        - ClientSignature (Name + Date)
        - CompanySignature (Vantix Name + Date)

DEFINE ScopeProtectionRules:
    - All changes must be classified before execution
    - Only BugFix and SmallChangeWithinTier are auto-included
    - All other classifications require quotation and written approval
    - Commercial terms must be documented before work begins
