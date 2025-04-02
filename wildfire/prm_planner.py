import math
import heapq
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
from scipy.ndimage import binary_dilation
from random import randrange, choice
import random
import time

def generate_valid_point(size):
    xsize, ysize = size
    return random.randint(0, xsize-1), random.randint(0, ysize-1)
def is_freespace(grid, point):
    if grid[point[0]][point[1]] == 0:
        return True
    return False
def distance(point1, point2):
    x0,y0 = point1
    x1,y1 = point2
    return math.sqrt( ((x1-x0)**2) +((y1-y0)**2))
def basic_line_bresenham(point1, point2):
    x0,y0 = point1
    x1,y1 = point2
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        points.append((x0, y0))  # Store the current point
        if x0 == x1 and y0 == y1:  # Stop when we reach the endpoint
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points

def line_collision_check(node0, node1, grid):
    line_points = basic_line_bresenham(node0, node1)
    for point in line_points:
        if grid[point[0]][point[1]] != 0:
            return False
        

    return True
def find_nearby(current_node, nodes, radius):
    neighbors = []
    for node in nodes:
        if node == current_node:
            continue
        if distance(current_node, node) <= radius:
            neighbors.append(node)
    return neighbors
def add_edge(graph_edges, node, neighbor, cost):
    if node not in graph_edges:
        graph_edges[node] = []
    graph_edges[node].append((neighbor, cost))

def prm_planner(grid, start, goal, num_samples=1000, connection_radius=20 ):
    xsize, ysize = len(grid), len(grid[0])
    size = (xsize, ysize)
    random_nodes = []
    graph_edges = {}
    random_nodes.append(start)
    random_nodes.append(goal)
    while len(random_nodes) < num_samples:
        x,y = generate_valid_point(size)
        if is_freespace(grid, (x,y)):
            random_nodes.append((x,y))
    for node in random_nodes:
        neighbors = find_nearby(node, random_nodes, connection_radius)
        for neighbor in neighbors:
            if line_collision_check(node, neighbor, grid):
                cost = distance(node, neighbor)
                add_edge(graph_edges, node, neighbor, cost)
                add_edge(graph_edges, neighbor, node, cost)
    path = astar(graph_edges, start, goal)

                 



        