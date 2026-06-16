"""
Logistics vertical demo data.
Single job: generate realistic trip manifests and fleet cost sheets
with seeded exceptions (loss-making routes, high fuel, late deliveries).
"""

import pandas as pd
import numpy as np

_RNG = np.random.default_rng(42)

_VEHICLES = ["VEH-001", "VEH-002", "VEH-003", "VEH-004"]
_VEHICLE_NAMES = {
    "VEH-001": "Toyota Hino 300",
    "VEH-002": "Isuzu NPR 400",
    "VEH-003": "MAN TGM 18.250",
    "VEH-004": "UD Quester 26.330",
}
_ROUTES = {
    "RT-JHB-CPT": ("Johannesburg", "Cape Town", 1400),
    "RT-JHB-DBN": ("Johannesburg", "Durban", 590),
    "RT-CPT-DBN": ("Cape Town", "Durban", 1750),
    "RT-JHB-PE":  ("Johannesburg", "Port Elizabeth", 1050),
    "RT-DBN-PE":  ("Durban", "Port Elizabeth", 680),
    "RT-JHB-BFN": ("Johannesburg", "Bloemfontein", 400),
}
_DRIVERS = ["J. Dlamini", "P. van der Berg", "S. Mokoena", "T. Pretorius", "R. Nkosi"]

# R per litre fuel (Apr 2026 approximate)
_FUEL_PRICE = 22.50
# Average consumption litres/100km
_L_PER_100 = {"VEH-001": 12, "VEH-002": 14, "VEH-003": 22, "VEH-004": 28}
# Toll per km (SA average)
_TOLL_PER_KM = 0.18
# Revenue per km (load rate)
_REVENUE_PER_KM = 9.50


def _fuel_cost(vehicle: str, km: float) -> float:
    return round(km * _L_PER_100[vehicle] / 100 * _FUEL_PRICE, 2)


def generate_demo() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Return (trip_manifest_df, {'fleet_costs': fleet_cost_df})."""

    rows = []
    trip_id = 1
    dates = pd.date_range("2026-03-01", "2026-03-31", freq="D")

    for d in dates:
        n_trips = _RNG.integers(1, 4)
        for _ in range(n_trips):
            vid = _RNG.choice(_VEHICLES)
            route_id = _RNG.choice(list(_ROUTES.keys()))
            origin, dest, base_km = _ROUTES[route_id]
            km = base_km * _RNG.uniform(0.97, 1.03)
            fuel = _fuel_cost(vid, km)
            toll = round(km * _TOLL_PER_KM, 2)
            revenue = round(km * _REVENUE_PER_KM, 2)
            driver = _RNG.choice(_DRIVERS)
            planned_hrs = round(km / 80, 1)
            actual_hrs  = round(planned_hrs * _RNG.uniform(0.9, 1.4), 1)
            on_time = actual_hrs <= planned_hrs * 1.15

            rows.append({
                "trip_id":      f"TR-{trip_id:04d}",
                "trip_date":    d.strftime("%Y-%m-%d"),
                "vehicle_id":   vid,
                "driver":       driver,
                "route_id":     route_id,
                "origin":       origin,
                "destination":  dest,
                "distance_km":  round(km, 1),
                "fuel_cost":    fuel,
                "toll_cost":    toll,
                "revenue":      revenue,
                "planned_hours": planned_hrs,
                "actual_hours":  actual_hrs,
                "on_time":      on_time,
            })
            trip_id += 1

    manifest_df = pd.DataFrame(rows)

    # Seed exceptions: 6 loss-making trips (revenue < costs), 4 very late
    for idx in _RNG.choice(len(manifest_df), 6, replace=False):
        manifest_df.at[idx, "fuel_cost"] = manifest_df.at[idx, "fuel_cost"] * 2.1
    for idx in _RNG.choice(len(manifest_df), 4, replace=False):
        manifest_df.at[idx, "actual_hours"] = manifest_df.at[idx, "planned_hours"] * 1.55
        manifest_df.at[idx, "on_time"] = False

    # Fleet cost sheet (one row per vehicle = monthly fixed costs)
    fleet_rows = []
    for vid, vname in _VEHICLE_NAMES.items():
        fleet_rows.append({
            "vehicle_id":    vid,
            "vehicle_name":  vname,
            "insurance":     _RNG.integers(3500, 6000),
            "maintenance":   _RNG.integers(2000, 5000),
            "depreciation":  _RNG.integers(4000, 8000),
            "licence_fees":  850,
        })

    fleet_df = pd.DataFrame(fleet_rows)

    return manifest_df, {"fleet_costs": fleet_df}
