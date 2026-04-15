// Pseudocode: Client-Hosted Deployment Patterns (No Vantix Servers)

DEFINE DeploymentPatterns:

    FUNCTION PatternA_Simple():
        Requirements:
            - Client provides agreed folder path
            - Standardised export file naming
            - Power BI dataset refresh uses client credentials OR service account controlled by client
            - Vantix receives least-privilege access (Viewer/Member as agreed)
        Pros:
            - Easy
            - Cheap
            - Low risk
        Cons:
            - File format drift may break refresh

    FUNCTION PatternB_SQL_DB():
        Requirements:
            - Client hosts SQL (Azure SQL OR on-prem)
            - Vantix connects via gateway per client policy
            - Schema fixed (Vantix provides mapping template)
            - Refresh schedule set by client OR jointly
        Pros:
            - Stable schema
            - Better quality
        Cons:
            - Requires database skills

    FUNCTION PatternC_AccountantReseller():
        Requirements:
            - Accounting firm standardises exports for multiple SMEs
            - Vantix ships identical dashboard pack per SME
        Pros:
            - Scale
            - Standardisation
        Cons:
            - Requires partner management

DEFINE Offboarding_Clean():
    IF ClientCancelsManaged:
        - End Vantix maintenance access (no sabotage)
        - Client retains data + tenant
        - Optional: Paid handover to internal staff
