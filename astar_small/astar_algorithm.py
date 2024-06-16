import numpy as np

from base_classes import Ship
from .astar_utils import AstarNode


def astar(astar_map, start_node, end_node, ice_class, ice_breaker=None, heuristic_func=None, search_tree=None, coef=None):
    ast = search_tree()
    steps = 0
    nodes_created = 1

    ship = Ship(19, ice_class, None, None, "Беда", None)
    start_i, start_j = astar_map.city2point[start_node]
    goal_i, goal_j = astar_map.city2point[end_node]
    estimated_dist = heuristic_func(astar_map.grid, (start_i, start_j), (goal_i, goal_j))

    
    start_node, goal_node = AstarNode(start_i, start_j), AstarNode(goal_i, goal_j, t=np.inf)
    ast.add_to_open(start_node)
    
    while not ast.open_is_empty():
        steps += 1
        cur_node = ast.get_best_node_from_open()
        if cur_node == goal_node:
            return (True, cur_node, steps, len(ast) + 2, list(set(ast.OPEN)) + list(ast.CLOSED), list(ast.CLOSED))
        if ast.was_expanded(cur_node):
            ast.add_dublicate()
            continue
            
        neighbours = astar_map.get_neighbours((cur_node.i, cur_node.j), ship, ice_breaker)
        for neighbour, (dist, time) in neighbours.items():
            new_node = AstarNode(
                neighbour[0], 
                neighbour[1], 
                parent=cur_node, 
                d=cur_node.d + dist,
                t=cur_node.t + time,
                h=heuristic_func(astar_map.grid, neighbour, (goal_i, goal_j)) / ship.speed
            )
            if coef and new_node.d > estimated_dist * coef:
                continue
            ast.add_to_open(new_node)
        ast.add_to_closed(cur_node)
        
    return (False, None, steps, nodes_created, None, ast.CLOSED)
