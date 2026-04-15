# Expected Commission Rules Guide (Rules-Based)

## Why rules-based
- Brokers need to trust and explain the numbers
- Providers often have known commission structures
- A simple model gets 80% of the benefit quickly

## Minimum inputs
- PolicyNumber
- Provider
- ProductType (or Plan)
- Adviser
- Premium (monthly or annual)
- PolicyStatus (Active/Lapsed)

## Rule types (choose what client can supply)
1) Provider + ProductType rate table
2) Provider + ProductType + Adviser split
3) Override rules (fixed fee, min/max, special cases)

## Time factors
- Initial commission: one-off (apply once, usually at inception month)
- Ongoing commission: recurring (apply monthly while active)

## Practical approach
Start with:
- Ongoing expected commission only (easiest)
Then add:
- Initial expected commission (if the data supports it)
