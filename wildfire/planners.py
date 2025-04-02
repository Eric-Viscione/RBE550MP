import math
import heapq
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
from scipy.ndimage import binary_dilation
import time
from grid import generate_name, create_directory
XY_RESOLUTION = 1.0
THETA_RESOLUTION = np.deg2rad(15)  # discretize angle 
STEP_SIZE = 1.0                    # distance per step
TURNING_RADIUS = 6.0               # approximate turning radius of car
MAX_STEER = np.deg2rad(30)         # maximum steering angle
GOAL_TOLERANCE = 1.0       # position tolerance in grid units
GOAL_THETA_TOLERANCE = np.deg2rad(6)  # angular tolerance
# TRAILER_SIZE = (4.0, 2.0) 
# CAR_SIZE = (2.0, 2.0)
TRAILER_GOAL_TOL = 5.0
WHEEL_BASE = 2.8



##node class to store the steering angle positions and search information
class Node:
    def __init__(self, x, y, theta, cost, parent, direction, vehicle_type, trailer_x=None, trailer_y=None):
        self.x = x          
        self.y = y          
        self.theta = theta  # Car orientation in radians
        self.cost = cost   
        self.parent = parent  
        self.direction = direction  # 1 for forward, -1 for reverse

        self.trailer_x = trailer_x if trailer_x is not None else x
        self.trailer_y = trailer_y if trailer_y is not None else y
        self.vehicle_type = vehicle_type
    def __lt__(self, other):
        return self.cost < other.cost

    def grid_index(self):
        ix = int(round(self.x / XY_RESOLUTION))
        iy = int(round(self.y / XY_RESOLUTION))
        itheta = int(round(self.theta / THETA_RESOLUTION)) % int(2 * math.pi / THETA_RESOLUTION)
        return (ix, iy, itheta)



def heuristic(node, goal, trailer=False):
    # Distance component
    dx = goal.x - node.x
    dy = goal.y - node.y
    d = math.hypot(dx, dy)
    
    w_theta = 1.0
    dtheta = w_theta * abs(angle_diff(goal.theta, node.theta))
    
    trailer_error = 0
    if trailer and hasattr(goal, 'trailer_x'):
        trailer_error = math.hypot(goal.trailer_x - node.trailer_x, goal.trailer_y - node.trailer_y)
    w_trailer = 1.0
    
    error = d + dtheta + w_trailer * trailer_error

    if node.direction == -1:
        reverse_penalty = 5 * d  
        error += reverse_penalty

    return error
##quick check for the tolerance of the final angle
def angle_diff(a, b):
    diff = a - b
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff

#bad and simple check to see if the vehcile has any sort of collision
def is_collision(x, y, grid):
    ix = int(round(x / XY_RESOLUTION))
    iy = int(round(y / XY_RESOLUTION))
    if ix < 0 or ix >= grid.shape[1] or iy < 0 or iy >= grid.shape[0]:
        return True
    return grid[iy, ix] == 1


def is_collision_with_radius(x, y, grid, radius):
    radius_cells = int(math.ceil(radius / XY_RESOLUTION))
    ix_center = int(round(x / XY_RESOLUTION))
    iy_center = int(round(y / XY_RESOLUTION))
    for dx in range(-radius_cells, radius_cells + 1):
        for dy in range(-radius_cells, radius_cells + 1):
            ix = ix_center + dx
            iy = iy_center + dy
            if ix < 0 or ix >= grid.shape[1] or iy < 0 or iy >= grid.shape[0]:
                return True
            cell_x = ix * XY_RESOLUTION
            cell_y = iy * XY_RESOLUTION
            if math.hypot(cell_x - x, cell_y - y) <= radius:
                if grid[iy, ix] == 1:
                    return True
    return False


def path_collision_check(x0, y0, x1, y1, grid):
    dist = math.hypot(x1 - x0, y1 - y0)
    steps = max(int(dist / (XY_RESOLUTION / 2)), 1)
    for i in range(steps + 1):
        u = i / steps
        x = x0 + u * (x1 - x0)
        y = y0 + u * (y1 - y0)
        if is_collision(x, y, grid):
            return True
    return False


def generate_successors_diwheel(current):

    successors = []
    
    move_directions = [ ##only moves left right up and down
        (1, 0),   
        (-1, 0),  
        (0, 1),
        (0, -1),  

    ]
    
    for dx, dy in move_directions:
        new_x = current.x + dx 
        new_y = current.y + dy 
        new_theta = 0
        
        cost = current.cost + 1

        new_node = Node(new_x, new_y, new_theta, cost, current, direction=1, vehicle_type="wheeled")
        successors.append(new_node)
    
    return successors

def generate_successors(current):
    successors = []
    for steer in np.linspace(-MAX_STEER, MAX_STEER, num=5):
        for direction in [1, -1]:
            if abs(steer) < 1e-4:  # Straight motion
                dx = STEP_SIZE * math.cos(current.theta) * direction
                dy = STEP_SIZE * math.sin(current.theta) * direction
                dtheta = 0.0
            else:
                radius = WHEEL_BASE / math.tan(steer)
                dtheta = (STEP_SIZE / radius) * direction
                dx = radius * (math.sin(current.theta + dtheta) - math.sin(current.theta))
                dy = -radius * (math.cos(current.theta + dtheta) - math.cos(current.theta))
            new_x = current.x + dx
            new_y = current.y + dy
            new_theta = (current.theta + dtheta) % (2 * math.pi)
            cost = current.cost + STEP_SIZE  
            
            new_node = Node(new_x, new_y, new_theta, cost, current, direction, vehicle_type=current.vehicle_type)
            successors.append(new_node)
    return successors


def hybrid_a_star(start, goal, grid, trailer=False, trailer_size=None):
    open_set = []
    visited = set()
    count = 0
    vehicle_type = start.vehicle_type
    # print(type(start), type(goal),start, goal)
    f_start = heuristic(start, goal)
    heapq.heappush(open_set, (f_start, count, start))
    
    while open_set:
        f, _, current = heapq.heappop(open_set)
        
        # Check if current state is within the goal region.
        if trailer:
            if (math.hypot(current.x - goal.x, current.y - goal.y) <= GOAL_TOLERANCE and
                abs(angle_diff(current.theta, goal.theta)) <= GOAL_THETA_TOLERANCE and
                math.hypot(current.trailer_x - goal.trailer_x, current.trailer_y - goal.trailer_y) <= TRAILER_GOAL_TOL):
                print("Goal reached!")
                return current
        else:
            if math.hypot(current.x - goal.x, current.y - goal.y) <= GOAL_TOLERANCE and abs(angle_diff(current.theta, goal.theta)) <= GOAL_THETA_TOLERANCE:
                print("Goal reached!")
                return current
        
        idx = current.grid_index()
        if idx in visited:
            continue
        visited.add(idx)
        if vehicle_type == "car": 
            for neighbor in generate_successors(current):
                if is_collision(neighbor.x, neighbor.y, grid):
                    continue
                if path_collision_check(current.x, current.y, neighbor.x, neighbor.y, grid):
                    continue
                count += 1
                f_neighbor = neighbor.cost + heuristic(neighbor, goal, trailer=False)
                heapq.heappush(open_set, (f_neighbor, count, neighbor))
        elif vehicle_type == "diwheel":   
            for neighbor in generate_successors_diwheel(current):
                if is_collision(neighbor.x, neighbor.y, grid)or (neighbor.x, neighbor.y) in visited:
                    continue
                count += 1
                f_neighbor = neighbor.cost + heuristic(neighbor, goal, trailer=False)
                heapq.heappush(open_set, (f_neighbor, count, neighbor))
        else:
                print(f"Invalid Vehicle Type {current.vehicle_type}")

                count += 1
                f_neighbor = neighbor.cost + heuristic(neighbor, goal, trailer=False)
                heapq.heappush(open_set, (f_neighbor, count, neighbor))
        
    print("No path found")
    return None


def reconstruct_path(goal_node):
    path = []
    node = goal_node
    while node:
        path.append((node.x, node.y, node.theta, node.direction))
        node = node.parent
    return path[::-1]

##Rendering functions
def visualize_path(path, grid, start, goal, car_size, trailer_size=None):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    plt.imshow(grid, cmap="Greys", origin="lower", extent=[0, grid.shape[1], 0, grid.shape[0]])
    
    if path is not None:
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        plt.plot(xs, ys, "-r", linewidth=2, label="Path")

        plt.legend()
    print(start)
    ax.plot(start[0], start[1], "go", markersize=8, label="Start")
    ax.plot(goal[0], goal[1], "bo", markersize=8, label="Goal")
    car_corners, trailer_corners = get_vehicle_corners(start[0], start[1],
                                                       start[2], car_size, trailer_size)
    car_patch = Polygon(car_corners, closed=True, color='blue', alpha=0.5)
    ax.add_patch(car_patch)
    
    trailer_patch = None
    if trailer_size is not None:
        trailer_patch = Polygon(trailer_corners, closed=True, color='green', alpha=0.5)
        ax.add_patch(trailer_patch)
    plt.title("Hybrid A* Path Planning")
    plt.xlabel("X")
    plt.ylabel("Y")
    
    plt.grid(True)
    plt.show()

def get_car_corners(x, y, theta, car_size):

    length, width = car_size
    hl = length / 2.0
    hw = width / 2.0

    corners = np.array([
        [ hl,  hw],
        [ hl, -hw],
        [-hl, -hw],
        [-hl,  hw]
    ])
    # Create a rotation matrix and rotate the corners
    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])
    rotated = np.dot(corners, R.T)
    rotated[:, 0] += x
    rotated[:, 1] += y
    return rotated

def get_vehicle_corners(x, y, theta, car_size, trailer_size, prev_trailer_theta=None):

    # Get the car's corners
    car_corners = get_car_corners(x, y, theta, car_size)
    
    if trailer_size is None:
        return car_corners, car_corners
    
    car_length, _ = car_size
    trailer_length, _ = trailer_size
    hitch_x = x - (car_length / 2.0) * math.cos(theta)
    hitch_y = y - (car_length / 2.0) * math.sin(theta)
    

    trailer_center_x = hitch_x - (trailer_length / 2.0) * math.cos(theta)
    trailer_center_y = hitch_y - (trailer_length / 2.0) * math.sin(theta)
    if prev_trailer_theta is None:
        prev_trailer_theta = theta
    trailer_theta = prev_trailer_theta + 0.5 * angle_diff(theta, prev_trailer_theta) 
    trailer_corners = get_car_corners(trailer_center_x, trailer_center_y, trailer_theta, trailer_size)
    
    return car_corners, trailer_corners

def animate_path(path, grid, car_size,vehicle_type, trailer_size=None):
    ##Portions of the animation code had parts written by Chatgpt 4omini to fix issues I was having with rendering a trailer
    fig, ax = plt.subplots(figsize=(8,8))
    ax.imshow(grid, cmap="Greys", origin="lower",
              extent=[0, grid.shape[1], 0, grid.shape[0]])
    
    # Plot the overall path 
    xs = [p[0] for p in path]
    ys = [p[1] for p in path]
    ax.plot(xs, ys, "-r", linewidth=1, label="Planned Path")
    ax.plot(xs[0], ys[0], "go", markersize=8, label="Start")
    ax.plot(xs[-1], ys[-1], "bo", markersize=8, label="Goal")
    ax.legend()

    car_corners, trailer_corners = get_vehicle_corners(path[0][0], path[0][1],
                                                       path[0][2], car_size, trailer_size)
    car_patch = Polygon(car_corners, closed=True, color='blue', alpha=0.5)
    ax.add_patch(car_patch)
    
    trailer_patch = None
    if trailer_size is not None:
        trailer_patch = Polygon(trailer_corners, closed=True, color='green', alpha=0.5)
        ax.add_patch(trailer_patch)
    
    def update(frame):
        car_corners, trailer_corners = get_vehicle_corners(path[frame][0],
                                                           path[frame][1],
                                                           path[frame][2],
                                                           car_size, trailer_size)
        car_patch.set_xy(car_corners)
        artists = [car_patch]
        if trailer_size is not None and trailer_patch is not None:
            trailer_patch.set_xy(trailer_corners)
            artists.append(trailer_patch)
        return artists

    ani = animation.FuncAnimation(fig, update, frames=len(path),
                                  interval=25, blit=True, repeat=False)
    
    
    plt.title("Path Planner")
    plt.show()
    save(ani, vehicle_type)
def save(ani, vehicle):
    answer = input("Save? y or n")
    directory = "temp"
    create_directory(directory)

    gif_name = generate_name(f"{vehicle} Path Plan", "gif")
    if answer == "y":
        print("Saving........")
        ani.save(f"{directory}/{gif_name}", writer='pillow', fps=10)
        print(f"Completed Saving {gif_name} to {directory}")
def cspace(grid, car_size, trailer_size=None):

    if trailer_size is not None:
        total_width = max(car_size[0], trailer_size[0])
        total_height = car_size[1] + trailer_size[1]
    else:
        total_width = int(car_size[0] / 2)
        total_height = int(car_size[1] / 2)
    kernel = np.ones((2 * total_height + 1, 2 * total_width + 1))
    inflated = binary_dilation(grid, structure=kernel).astype(int)
    return inflated
def ackerman_planner(start,goal, grid, vehicle_size):
    start_time = time.time()

    start_node = Node(x=start[0], y=start[1], theta=np.deg2rad(start[2]), cost=0.0, parent=None, direction=1, vehicle_type="car")
    goal_node = Node(x=goal[0], y=goal[1], theta=np.deg2rad(goal[2]), cost=0.0, parent=None, direction=1, vehicle_type="car")
    inflated_grid = cspace(grid, vehicle_size)
    path = hybrid_a_star(start_node, goal_node, inflated_grid)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Planned path in {elapsed_time} seconds")
    if path:
        path = reconstruct_path(path)
        animate_path(path, grid, vehicle_size, vehicle_type="Ackerman Car")
    else:
        visualize_path(None, grid, start, goal, vehicle_size)



def diwheel_planner(start,goal, grid, vehicle_size):
    start_time = time.time()

    start_node = Node(x=start[0], y=start[1], theta=np.deg2rad(start[2]), cost=0.0, parent=None, direction=1, vehicle_type="diwheel")
    goal_node = Node(x=goal[0], y=goal[1], theta=np.deg2rad(goal[2]), cost=0.0, parent=None, direction=1, vehicle_type="diwheel")
    inflated_grid = cspace(grid, vehicle_size)
    path = hybrid_a_star(start_node, goal_node, inflated_grid)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Planned path in {elapsed_time} seconds")
    if path:
        path = reconstruct_path(path)
        animate_path(path, grid, vehicle_size, vehicle_type="Diwheel")
    else:
        visualize_path(None, grid, start, goal, vehicle_size)
if __name__ == '__main__':
    GRID_WIDTH = 120
    GRID_HEIGHT = 120
    grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)

    car_size = (7,2)
    start = Node(x=5.0, y=5.0, theta=np.deg2rad(0), cost=0.0, parent=None, direction=1)
    goal = Node(x=55.0, y=55.0, theta=np.deg2rad(220), cost=0.0, parent=None, direction=1)
    grid
    
    inflated_grid = cspace(grid, car_size=(7,2))
    
    goal_node = hybrid_a_star(start, goal, inflated_grid)
    if goal_node:
        path = reconstruct_path(goal_node)
        print("Path length:", len(path))
        # visualize_path(path, inflated_grid)
        animate_path(path, grid, car_size)
