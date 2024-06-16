import pandas as pd
from dataclasses import dataclass


# SHIPS

@dataclass
class Ship:
    speed: float
    ice_class: int
    departure: str
    arrival: str
    name: str
    start_date: pd.Timestamp


def edge_time(start_point, end_point, ship, astar_map, nodes_path, ice_breaker_id=None):
    if ice_breaker_id is None:
        ice_breaker_id = 3
    assert ice_breaker_id <= 3, "Invalid ice breaker ID!"

    ic = ship.ice_class
    if 4 <= ic <= 6:
        ic = 4
    paths = nodes_paths.get((ic, ice_breaker_id), {})
    if (start_point, end_point) not in paths:
        return None, np.inf

    nodes = paths[(start_point, end_point)]
    ice_breaker = ice_breakers[ice_breaker_id] if ice_breaker_id < 3 else None

    dist, time = 0, 0
    for i in range(len(nodes) - 1):
        for ice_value, dist_km in astar_map.info_edges[node][next_node].items():
            v = correct_speed(ship, ice_value, ice_breaker=ice_breaker)
            if v == 0:
                return None, np.inf
            time += dist_km / 1.852 / v
            dist += dist_km / 1.852
    return dist, time


def map_ice_class(ice_class):
    if ice_class.lower() == "нет":
        return 0
    else:
        ic = int(ice_class[4:])
        if ic == 7 or ic == 9:
            return ic
        elif 4 <= ic <= 6:
            return 4
        else:
            raise ValueError("Invalid ship's ice class value!")


def correct_speed(ship: Ship, ice_value, ice_breaker: Ship = None):
    """
    Calculates certain ship speed depending on an ice class, ice heaviness and
    ice breaker escort
    """
    
    if ice_value < 10:
        return 0

    ice_breaker_speed = None
    if ice_breaker is not None:
        if ice_value >= 20:
            ice_breaker_speed = ice_breaker.speed
        elif ice_value >= 15:
            ice_breaker_speed = ice_value * 0.9 if ice_breaker.name in ("Таймыр", "Вайгач") else ice_value
        elif ice_value >= 10:
            ice_breaker_speed = ice_value * 0.75 if ice_breaker.name in ("Таймыр", "Вайгач") else ice_value
            
    if ice_value >= 20:
        return ship.speed if ice_breaker is None else min(ship.speed, ice_breaker_speed)
    elif ice_value >= 15:
        if ship.ice_class < 4:
            return 0
        elif 4 <= ship.ice_class <= 6:
            return 0 if ice_breaker is None else min(ship.speed * 0.8, ice_breaker_speed)
        elif ship.ice_class == 7:
            return ship.speed * 0.6 if ice_breaker is None else min(ship.speed, ice_breaker_speed)
        elif ship.ice_class == 9:
            return ice_value * 0.9 if ship.name in ("Таймыр", "Вайгач") else ice_value
    elif ice_value >= 10:
        if ship.ice_class < 4:
            return 0
        elif 4 <= ship.ice_class <= 6:
            return 0 if ice_breaker is None else min(ship.speed * 0.7, ice_breaker_speed)
        elif ship.ice_class == 7:
            return 0 if ice_breaker is None else min(ship.speed * 0.8, ice_breaker_speed)
        elif ship.ice_class == 9:
            return ice_value * 0.75 if ship.name in ("Таймыр", "Вайгач") else ice_value