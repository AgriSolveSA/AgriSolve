// Pseudocode: 90-Day Execution Plan (Risk-Averse, Asynchronous, Template-First)

DEFINE Objective:
    - Build repeatable, client-hosted Power BI dashboard product
    - Generate predictable cashflow with minimal weekly time

DEFINE CoreConstraints:
    - FullyEmployed = TRUE (no daytime meetings)
    - CommunicationMode = Asynchronous (written first, calls only if unavoidable)
    - TemplateDriven = TRUE (same model/pages for all clients in vertical)
    - ClientHosted = TRUE (data stays in client tenant/storage)
    - IPProtected = TRUE (templates remain AgriSolve IP unless Buy-Out)

STATE 0: ReadyToSell
    Gate = "No improvisation"
    Deliverables:
        - DemoPBIX (≤6 pages)
        - IntakeChecklist + DataMappingTemplate
        - PricingTiers finalized (Starter/Standard/Buy-Out)
        - ChangeControlTemplate ready
        - ServiceAgreement + POPIAOperatorAgreement templates ready
        - OnboardingEmailSequence ready
    PassCondition:
        - Client onboarding requires no new pages/tables/promises

STATE 1: StandardPackBuilt
    Gate = "Runs for 7 days"
    WorkItems:
        - Pick ONE vertical for standardization
        - Lock KPI list + definitions
        - Build star schema + measures library
        - Implement refresh pattern (SharePoint exports or SQL)
        - Publish in test tenant/workspace
    PassCondition:
        - Scheduled refresh succeeds for 7 days without manual babysitting

STATE 2: Productised
    Gate = "Quote + onboard in 30 min admin"
    WorkItems:
        - Create 1-page offer + package selector
        - Create monthly management pack template (PDF + commentary)
        - Define SLA + included changes per tier
        - Define OutOfScope list
    PassCondition:
        - Quote, contract, intake checklist, kickoff email in <30 minutes

STATE 3: ControlledRevenue
    Gate = "<1 hour/week per client"
    Target:
        - First 1–3 paying clients with clean data
    Rules:
        - Accept only clients with standard exports
        - Written comms only
        - No custom pages
        - All requests via Change Control
    PassCondition:
        - Each client runs with <1 hour/week support + predictable refresh

STATE 4: StableAndScalable
    Gate = "Disappear 7 days"
    Target:
        - 5–10 clients OR 1 accountant partner placing into 5+ SMEs
    WorkItems:
        - Standardize exports harder (reduce variability)
        - Build Top20Failures troubleshooting runbook
        - Build partner referral playbook for accountants
        - Add quarterly review upsell
    PassCondition:
        - Can disappear for 7 days without critical breakage

DEFINE RevenueSafetyGates:
    - Do not plan unpaid leave until:
        Condition1: RecurringRevenue ≥ 50% MonthlyBurn
        Condition2: BusinessCashBuffer ≥ 2–3 months burn
        Condition3: OpsRunbook exists + refresh failure response templated
