import geopy
import numpy as np
import pandas as pd
import shapely as sh
import geopandas as gpd
from geopy.distance import distance as Distance
from tqdm import tqdm


IceWeights = dict[int, dict[int, float]]


def addKm(lat: float, lon: float, km: float, bearing: float):
    # Define starting point.
    start = geopy.Point(longitude=lon, latitude=lat)

    # Define a general distance object, initialized with a distance of 1 km.
    d = Distance(kilometers=km)

    # Use the `destination` method with a bearing of 0 degrees (which is north)
    # in order to go from point `start` 1 km to north.
    dest = d.destination(point=start, bearing=bearing)
    return dest.latitude, dest.longitude


def polygonFromCorner(lat: float, lon: float):
    lat1, lon1 = lat, lon
    lat2, lon2 = addKm(lat, lon, 25, 180)
    lat3, lon3 = addKm(lat, lon, 25, 90)
    lat4, lon4 = addKm(lat3, lon3, 25, 180)
    return sh.Polygon(((lon1, lat1), (lon3, lat3), (lon4, lat4), (lon2, lat2)))


def computeIceGrid(latitudes: np.ndarray, longitudes: np.ndarray) -> gpd.GeoDataFrame:
    assert latitudes.shape == longitudes.shape
    polygons = [
        polygonFromCorner(latitudes[i, j], longitudes[i, j])
        for i, j in np.ndindex(latitudes.shape)
    ]
    return gpd.GeoDataFrame(geometry=polygons)


def computeIceWeights(grid: gpd.GeoDataFrame, iceGrid: gpd.GeoDataFrame) -> IceWeights:
    iceBounds = np.row_stack([sh.bounds(cell) for cell in iceGrid.geometry])
    iceMinBounds = iceBounds[:, (0, 1)]
    iceMaxBounds = iceBounds[:, (2, 3)]

    iceGridWeights: IceWeights = {i: {} for i in grid.index}

    for id, cell in tqdm(zip(grid.index, grid.geometry)):
        sh.prepare(cell)
        minX, minY, maxX, maxY = sh.bounds(cell)
        inUpperBound = np.all(iceMinBounds <= (maxX, maxY), axis=1)
        inLowerBound = np.all((minX, minY) <= iceMaxBounds, axis=1)

        filteredCells = iceGrid.loc[inUpperBound & inLowerBound]
        for j, iceCell in filteredCells.geometry.items():
            if cell.intersects(iceCell):
                intersectionArea = cell.intersection(iceCell)
                r = intersectionArea.area / cell.area
                iceGridWeights[id][j] = r

    return iceGridWeights


def fillIceData(grid: gpd.GeoDataFrame, weights: IceWeights, iceValues: np.ndarray):
    """ Добавляет значения ice в таблицу grid

    grid: Финальная сетка
    weights: Посчитанные веса ячеек со льдом из датасета
    iceValues: Выпрямленный массив значений то есть (5, 10) -> (50, 1)
    """

    grid["ice"] = 0

    for id in grid.index:
        for j, r in weights[id].items():
            grid.at[id, "ice"] += iceValues[j] * r
