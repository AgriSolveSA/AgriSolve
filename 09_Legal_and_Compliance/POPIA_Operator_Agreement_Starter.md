// Pseudocode: POPIA Operator Agreement Starter (Template)

DEFINE AgreementPurpose:
    - Operator = Vantix
    - ResponsibleParty = Client
    - Scope = Processing personal information only to deliver dashboard service

DEFINE CoreClauses:
    Clause1: PurposeLimitation
        - Process data only for dashboard delivery
    Clause2: SecuritySafeguards
        - Least privilege access
        - Confidentiality obligations
        - Access control enforcement
        - Incident handling procedures
    Clause3: SubOperators
        - Declare if third parties are used
    Clause4: BreachNotification
        - Define timelines + process for notifying Responsible Party
    Clause5: DataRetentionAndDeletion
        - Specify retention rules
        - Define deletion process upon termination
    Clause6: AuditAndAssurance
        - Provide reasonable cooperation for audits

DEFINE References:
    - POPIA guidance + Operator agreement discussions
    - Broader data protection summaries
    - POPIA text (official)

DEFINE PracticalStance_ClientHostedModel:
    - Client retains hosting + primary security control
    - Vantix access = least privilege + revocable
    - All artifacts stored in client tenant unless explicitly agreed otherwise
