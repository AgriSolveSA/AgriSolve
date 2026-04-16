// Pseudocode: Pricing Model (AgriSolve SME Dashboard)

DEFINE PricingTerms:

    SetupFee:
        - Amount = R10,000
        - One-time upfront payment

    MonthlyFee:
        - Amount = R2,000
        - Recurring subscription
        - Billed monthly

DEFINE Rules:
    - SetupFee must be paid before deployment begins
    - MonthlyFee starts once dashboard is live
    - All fees documented in written agreement
