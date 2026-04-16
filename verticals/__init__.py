"""
Vertical registry.

app.py imports only REGISTRY — no vertical-specific code ever appears
in the UI layer. Add new verticals here as they are implemented.
"""

from verticals.insurance_broker.vertical import InsuranceBrokerVertical

REGISTRY: dict[str, type] = {
    "Insurance Broker": InsuranceBrokerVertical,
}
