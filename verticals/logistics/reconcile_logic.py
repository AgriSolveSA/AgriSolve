"""
Logistics reconciliation logic.
Single job: detect exceptions in trip manifests against fleet cost data
and return them in the VerticalBase standard column format.

Exception types:
    LOSS_MAKING_TRIP  — revenue < variable costs (fuel + toll)
    HIGH_FUEL_COST    — fuel cost > 40% of revenue
    LATE_DELIVERY     — actual_hours > planned_hours * 1.15
    UNREGISTERED_VEH  — vehicle_id not in fleet cost sheet
"""

import pandas as pd


def run_reconciliation(
    manifest_df: pd.DataFrame,
    secondaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    fleet_df = secondaries.get("fleet_costs", pd.DataFrame())
    registered_vehicles = set(fleet_df["vehicle_id"]) if not fleet_df.empty else set()

    exceptions: list[dict] = []

    for _, row in manifest_df.iterrows():
        variable_cost = row["fuel_cost"] + row["toll_cost"]
        revenue       = row["revenue"]
        margin        = revenue - variable_cost
        fuel_pct      = row["fuel_cost"] / revenue if revenue > 0 else 1.0
        late_ratio    = row["actual_hours"] / row["planned_hours"] if row["planned_hours"] > 0 else 1.0

        # Loss-making trip
        if margin < 0:
            exceptions.append({
                "entity_id":      row["trip_id"],
                "counterparty":   row["vehicle_id"],
                "description":    f"{row['route_id']} · {row['driver']}",
                "exception_type": "LOSS_MAKING_TRIP",
                "severity":       "High",
                "variance":       round(margin, 2),
                "trip_date":      row["trip_date"],
                "distance_km":    row["distance_km"],
                "revenue":        round(revenue, 2),
                "variable_cost":  round(variable_cost, 2),
            })
        # High fuel cost (>40% of revenue, but not already flagged as loss-making)
        elif fuel_pct > 0.40:
            exceptions.append({
                "entity_id":      row["trip_id"],
                "counterparty":   row["vehicle_id"],
                "description":    f"{row['route_id']} · {row['driver']}",
                "exception_type": "HIGH_FUEL_COST",
                "severity":       "Medium",
                "variance":       round(row["fuel_cost"] - revenue * 0.30, 2),
                "trip_date":      row["trip_date"],
                "distance_km":    row["distance_km"],
                "revenue":        round(revenue, 2),
                "variable_cost":  round(variable_cost, 2),
            })

        # Late delivery
        if late_ratio > 1.15:
            exceptions.append({
                "entity_id":      row["trip_id"],
                "counterparty":   row["vehicle_id"],
                "description":    f"{row['route_id']} · {row['driver']}",
                "exception_type": "LATE_DELIVERY",
                "severity":       "Medium" if late_ratio < 1.4 else "High",
                "variance":       round(row["actual_hours"] - row["planned_hours"], 2),
                "trip_date":      row["trip_date"],
                "distance_km":    row["distance_km"],
                "revenue":        round(revenue, 2),
                "variable_cost":  round(variable_cost, 2),
            })

        # Unregistered vehicle
        if registered_vehicles and row["vehicle_id"] not in registered_vehicles:
            exceptions.append({
                "entity_id":      row["trip_id"],
                "counterparty":   row["vehicle_id"],
                "description":    f"Vehicle not in fleet cost sheet · {row['driver']}",
                "exception_type": "UNREGISTERED_VEH",
                "severity":       "Low",
                "variance":       0.0,
                "trip_date":      row["trip_date"],
                "distance_km":    row["distance_km"],
                "revenue":        round(revenue, 2),
                "variable_cost":  round(variable_cost, 2),
            })

    if not exceptions:
        return pd.DataFrame(columns=[
            "entity_id", "counterparty", "description",
            "exception_type", "severity", "variance",
            "trip_date", "distance_km", "revenue", "variable_cost",
        ])

    return pd.DataFrame(exceptions)
