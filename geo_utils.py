import numpy as np
from shapely.affinity import scale
from geopy.distance import geodesic


def get_close_points(i, j, grid, dx=0.1, dy=0.1, xfact=1.1, yfact=1.1):
    point_min_x, point_min_y, point_max_x, point_max_y = grid.loc[i, j].geometry.bounds
    
    points_ = grid[(grid.geometry.bounds.maxx > point_min_x - dx)]
    points_ = points_[(points_.geometry.bounds.minx < point_max_x + dx)]
    
    points_ = points_[(points_.geometry.bounds.maxy > point_min_y - dy)]
    points_ = points_[(points_.geometry.bounds.miny < point_max_y + dy)]
    points_ = points_[points_.geometry.intersects(scale(grid.loc[i, j].geometry, xfact=xfact, yfact=yfact))]
    return points_


def get_length(lat1, lon1, lat2, lon2):
    # Earth's radius in kilometers
    radius = 6371.0

    def radians(degrees):
        return np.pi * degrees / 180.

    # Convert latitude and longitude to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Calculate the differences between the coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Apply the Haversine formula
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = radius * c

    # Calculate the x and y coordinates in kilometers
    x = distance * np.cos(lat2_rad) * np.cos(lon2_rad - lon1_rad)
    y = distance * np.cos(lat2_rad) * np.sin(lon2_rad - lon1_rad)

    return np.sqrt(x ** 2 + y ** 2)


def intersection_to_length(intersection):
    lat1, lat2 = intersection.coords.xy[0]
    lon1, lon2 = intersection.coords.xy[1]
    return geodesic((lat1, lon1), (lat2, lon2))
    # return get_length(lat1, lon1, lat2, lon2)