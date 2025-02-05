import heapq
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
directions = [
    (-1, 0),    #North
    (1,  0),    #south
    (0, -1),    #left 
    (0,  1)     #right
]
debug = False
def grid_to_graph(grid_map):
    valid_locations = [0, 2, 4]
    rows = len(grid_map)
    cols = len(grid_map[0])
    graph = defaultdict(list)

    for r in range(rows):
        for c in range(cols):
            if grid_map[r][c] in valid_locations:  # Only if current cell is free or the goal
                node = (r, c)
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < rows and 0 <= nc < cols and grid_map[nr][nc] in valid_locations): 
                        graph[node].append((nr, nc))
    if debug:
        for node, neighbors in graph.items():
            print(f"{node}: {neighbors}")
        visualize_grid(graph)

    return graph
def visualize_grid(graph):

    G = nx.Graph()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            G.add_edge(node, neighbor)
    
    # Visualize the graph using Matplotlib
    pos = {node: (node[1], -node[0]) for node in G.nodes()}  # Positioning nodes (flipping Y to match visual style)
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10)
    
    plt.show()
def is_valid(x, y, grid_row, grid_col):
    return 0 <= x < grid_row and 0 <= y < grid_col

def is_obstacle(row, col, map_world):
    return map_world[row][col] == 1

def manhattan_distance(a, b):
    distance = abs(a[0] - b[0]) + abs(a[1] - b[1])
    return distance

def a_star_search(start, goal, map_world):
    """A* search algorithm for pathfinding in the graph. Adapted from geeksforgeeks.com"""
    maps_rows = len(map_world)
    map_cols = len(map_world[0]) 
    if not is_valid(start[0], start[1], maps_rows, map_cols) or not is_valid(goal[0], goal[1], maps_rows, map_cols):
         #check if the start and destination are within the bounds of the map(should always be but good to check)
        print("Source or destination is invalid")
        return
    if is_obstacle(start[0], start[1], map_world) or is_obstacle(goal[0], goal[1], map_world):
        print("There is no valid path to the goal! The hero gets lost and loses!")
        # print("The starting or goal position is inside an obstacle, invalid map!")
        return None
    path_back = {start: None}  
    graph = grid_to_graph(map_world)
    num_tries = 0
    while goal not in path_back:
        if num_tries > 10:
            break
        pq = []  # queue
        heapq.heappush(pq, (0, start))  #Add the start node to the heap because we always start there
         
        cost_so_far = {start: 0}

        while pq:
            _ , current = heapq.heappop(pq) #find the next node and make it the current one

            if current == goal:  #goal found
                break  

            for neighbor in graph[current]:
                new_cost = cost_so_far[current] + 1  # 1 is the cost for now, but will add cost based on distance from enemies
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + manhattan_distance(neighbor, goal) #priority path = cost so far + manhattan distance to the goal
                    heapq.heappush(pq, (priority, neighbor)) #add this to the heap then add the next one to the path
                    path_back[neighbor] = current
        num_tries += 1

    if goal not in path_back:
        print("No Path Found")  
        return None
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = path_back[current]
    path.reverse()
    
    return path if path[0] == start else []  # Return path or empty if unreachable
