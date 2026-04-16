"""
Vertical registry.

app.py imports only REGISTRY — no vertical-specific code ever appears
in the UI layer. Add new verticals here as they are implemented.
"""

from verticals.insurance_broker.vertical import InsuranceBrokerVertical
from verticals.accounting.vertical import AccountingVertical
from verticals.construction.vertical import ConstructionVertical

REGISTRY: dict[str, type] = {
    "Insurance Broker": InsuranceBrokerVertical,
    "Accounting Firm":  AccountingVertical,
    "Construction":     ConstructionVertical,
}
