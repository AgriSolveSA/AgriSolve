# Expected Commission Model (v6.3)

Goal: turn "commission leakage" into a **number** by calculating Expected Commission
and comparing to Actual Commission statement lines.

This is intentionally **rules-based** (not ML) so it is:
- explainable to brokers
- auditable
- maintainable
- fast to implement across clients

Core idea:
ExpectedCommission = Premium * Rate * Split * TimeFactor (+ overrides)
