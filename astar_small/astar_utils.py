
import numpy as np
from collections import defaultdict
from tqdm.notebook import tqdm
import heapq

from base_classes import Ship, correct_speed
from geopy.distance import geodesic


class AstarMap:
    @staticmethod
    def _km2seamile(d):
        return d / 1.852

    def __map_cities(self, data_graph_points):
        self.city2point = {}
        self.point2city = {}
        for city_id, pt in zip(self.cities, self.cities.index):
            self.point2city[pt] = data_graph_points.loc[city_id].point_name
            self.city2point[data_graph_points.loc[city_id].point_name] = pt
    
    def __init__(self, geom_grid, city_grid, edges, data_graph_points):
        self.grid = geom_grid
        self.cities = city_grid[city_grid.notna()]
        self.edges = edges
        self.info_edges = defaultdict(lambda: {})
        self.__map_cities(data_graph_points)

    def map_ice(self, ice_grid):
        self.info_edges = defaultdict(lambda: {})
        for vertex1 in tqdm(self.edges):
            for vertex2 in self.edges[vertex1]:
                edge_ice = defaultdict(float)
                traversable = True
                for mid_vertex in self.edges[vertex1][vertex2]:
                    if ice_grid.loc[mid_vertex] < 10:
                        traversable = False
                        break
                    edge_ice[ice_grid.loc[mid_vertex]] += self.edges[vertex1][vertex2][mid_vertex]
                if traversable:
                    self.info_edges[vertex1][vertex2] = edge_ice.copy()
    
    def get_neighbours(self, vertex, ship, ice_breaker=None):
        ship_edges = {}
        for dst in self.info_edges[vertex]:
            distance, time = 0, 0
            for ice_value, dist_km in self.info_edges[vertex][dst].items():
                v = correct_speed(ship, ice_value, ice_breaker=ice_breaker)
                if v == 0:
                    time = np.inf
                    break
                time += self._km2seamile(dist_km) / v
                distance += self._km2seamile(dist_km)
            if time != np.inf:
                ship_edges[dst] = (distance, time)
        return ship_edges
    

class AstarNode:
    def __init__(self, i, j, d=0, t=0, h=0, f=None, parent=None, tie_breaking_func=None):
        self.i = i
        self.j = j
        self.d = d
        self.t = t
        self.h = h
        if f is None:
            self.f = self.t + self.h
        else:
            self.f = f        
        self.parent = parent
    
    def __eq__(self, other):
        return (self.i == other.i) and (self.j == other.j)
    
    def __hash__(self):
        return hash((self.i, self.j))

    def __lt__(self, other): 
        return self.f < other.f


class AstarTree:
    def __init__(self):
        self._open = []
        heapq.heapify(self._open)
        self._closed = set()
        self._enc_open_dublicates = 0
        
    def __len__(self):
        return len(self._open) + len(self._closed)
                    
    def open_is_empty(self):
        return len(self._open) == 0
  
    def add_to_open(self, item):
        heapq.heappush(self._open, item)
        return    
    
    def get_best_node_from_open(self):
        return heapq.heappop(self._open)      

    def add_to_closed(self, item):
        self._closed.add(item)

    def was_expanded(self, item):
        return item in self._closed
    
    def add_dublicate(self):
        self._enc_open_dublicates += 1

    @property
    def OPEN(self):
        return self._open
    
    @property
    def CLOSED(self):
        return self._closed

    @property
    def number_of_open_dublicates(self):
        return self._enc_open_dublicates


def heuristic(grid, node: tuple, goal: tuple):
    cur_lon, cur_lat = grid.loc[node].centroid.xy
    goal_lon, goal_lat = grid.loc[goal].centroid.xy
    return geodesic((cur_lat[0], cur_lon[0]), (goal_lat[0], goal_lon[0])).km


def get_path(node: AstarNode):
    path = []
    while node:
        path.append((node.i, node.j))
        node = node.parent
    return path[::-1]
