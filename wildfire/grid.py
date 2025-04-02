import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib
from random import randrange, choice
import random
from dataclasses import dataclass
import argparse
import os
import datetime

@dataclass
class dirMapping: #maps a random(0-3) to x and y directions +/-1 and also stores the oppisite value we dont want to generate
    value: int
    x: int
    y: int
    inverse: int


mapping = [
    dirMapping(0, 1, 0, 1),
    dirMapping(1, -1, 0, 0),
    dirMapping(2, 0, 1, 3),
    dirMapping(3, 0, -1, 2)
]


    


class generate_graph:
    def __init__(self, xlim, ylim, coverage,square_size = 1 ,obstacle_size = 4):
        self.coverage = coverage
        self.xlim = xlim
        self.ylim = ylim
        self.square_size = square_size        
        self.x_start = 0
        self.y_start = 0
        self.obstacle_size = obstacle_size
        self.prev_dir = 0
        
        self.corner_array = np.zeros((self.xlim+1, self.ylim+1), dtype=int)

    def make_grid(self,coverage=0.1, obstacle_size=None):
        """Generates the array and size of the obstacle course, plots the course
        """
        xsize, ysize = self.xlim, self.ylim
        self.array = np.zeros((xsize, ysize), dtype=int) 
        num_shapes = int((coverage * ((xsize) * (ysize)) / (self.square_size ** 2))/4)+1
        # num_shapes = 2
        print(f"The number of shapes is {num_shapes}")
        for _ in range(num_shapes):
            self.create_shape()
        # self.generate_corner_graph()
        # start, goal = self.start_and_goal()
        return self.array

        
         
        
        return self.array
    def choose_open_spot(self):
        open_positions = list(zip(*np.where(self.array == 0))) 
        
        if not open_positions:
            return [0,0]
        
        return random.choice(open_positions)  

    def create_shape(self):
        """Randomly seeds a shape that has and area of self.obstacle_size 
            The squares grow from the inital seed in a random direction
            The shape is stored by its starting corner in the array of the entire map
        """
        try:
            start_pos = self.choose_open_spot()
        except ValueError as e:
            print(f"Error: {e}")
            return
        self.x_start, self.y_start = start_pos
        self.array[self.x_start, self.y_start] = 1
        self.prev_dir = None
        for _ in range(self.obstacle_size -1):         #randomly increment in one direction frrom the previous rectangle, adding it to the graph. when you get to 3 new rectangles stop       
            self.choose_dir(self.prev_dir)
            if self.x_start >= self.xlim:
                self.x_start = self.xlim-1
            if self.y_start >= self.ylim:
                self.y_start = self.ylim-1
            self.array[self.y_start, self.x_start] = 1
    def choose_dir(self, check_dir):
        """Generate a starting point that goes in a random direction away from the starting point
           Also checks to ensure the random starting point does not double back on an already exisiting square

        Args:
            check_dir (int): The direction of the previously called square, to check for the doubling back condition
        """
        invalid_dir = None
        if check_dir is not None:    
            invalid_dir_check = next((entry for entry in mapping if entry.value == check_dir))
            if invalid_dir_check:
                invalid_dir = invalid_dir_check.value

        valid_dirs = list(range(self.obstacle_size))
        if invalid_dir is not None and invalid_dir in valid_dirs:
            valid_dirs.remove(invalid_dir)  # Only remove if check_dir is in valid_dirs   
        rand_num = choice(valid_dirs)
        direction = next((entry for entry in mapping if entry.value == rand_num))         #update the x_start and y_Start
        if direction:
            self.x_start = self.x_start + direction.x
            self.y_start = self.y_start + direction.y
    
            self.prev_dir = direction.inverse

def start_and_goal(self, grid, invalid_locations , goal_distance = 5,):
    open_x, open_y = np.where(np.isin(grid, invalid_locations, invert=True))
    if len(open_x) == 0 or len(open_y) == 0:
        print("No valid start and goal positions found.")
        return None, None  # Safely return without crashing
    while True:
        start_idx = random.choice(range(len(open_x)))  
        start_x, start_y = open_x[start_idx], open_y[start_idx]
        valid_goals = []
        for x, y in zip(open_x, open_y):
            if abs(x - start_x) >= goal_distance or abs(y - start_y) >= goal_distance:
                valid_goals.append((x, y))
        if not valid_goals:
            print(f"No valid goals found for start position ({start_x}, {start_y}). Returning None.")
            return None, None 
        
        goal_x, goal_y = random.choice(valid_goals)
        if not is_obstacle(start_x, start_y, grid) and not is_obstacle(goal_x, goal_y, grid):
            return (int(start_y), int(start_x)), (int(goal_y), int(goal_x))
        print("Recalculating goals")
    # @staticmethod
def is_obstacle(row, col, map_world):
    return map_world[row][col] == 1
   

def pixelize_grid(grid, scale_factor):

    expanded_grid = np.kron(grid, np.ones((scale_factor, scale_factor)))
    return expanded_grid

def make_defined_grid(size, start, end, vehicle_size, obstacles=None, rand_obstacles=0,rand_number=5, simple=True):
    xsize, ysize = size
    xstart, ystart = start
    xend, yend= end
    array = np.zeros((xsize, ysize), dtype=int)
    if simple:
        array[
            xstart - (vehicle_size[1] // 2) : xstart + (vehicle_size[1] // 2),
            ystart - (vehicle_size[0] // 2) : ystart + (vehicle_size[0] // 2)
        ] = 4
        array[
            xend - (vehicle_size[1] // 2) : xend + (vehicle_size[1] // 2),
            yend - (vehicle_size[0] // 2) : yend + (vehicle_size[0] // 2)
        ] = 4
        array[xstart][ystart] = 2
        array[xend][yend] = 3
    
    #obstacles are stored in [x1, y1, x2,y2] representing rectangles
    max_obstacle_size = (int(xsize/10), int(ysize/10))
    if rand_obstacles:
        rand_obstacles = generate_random_obstacles((xsize, ysize), rand_number, max_obstacle_size)
        obstacles.extend(rand_obstacles)
    for obstacle in obstacles:
        array[obstacle[0]:obstacle[2], obstacle[1]:obstacle[3]] = 1

    return array
def generate_random_obstacles(grid_size, num_obstacles, max_obstacle_size):

    obstacles = []
    xsize, ysize = grid_size
    # print(int(xsize/6))
    for _ in range(num_obstacles):
        x1 = random.randint(int(xsize/6), xsize - int(1.5*(xsize/6)))
        y1 = random.randint(int(ysize/6), ysize - int(1.5*(ysize/6)))
        
        x2 = random.randint(x1, min(x1 + max_obstacle_size[0], xsize - 1))  # Ensure x2 is within grid bounds
        y2 = random.randint(y1, min(y1 + max_obstacle_size[1], ysize - 1))  # Ensure y2 is within grid bounds
        
        obstacles.append([x1, y1, x2, y2])
    
    return obstacles
def create_directory(path = None):
    # if path == None:
    #     path = directory
    # else:
    path = f'{path}'
    try: ##directory creation references from geeksforgeeks.com
        os.mkdir(path)
        print(f"Directory '{path}' created successfully.")
    except FileExistsError:
        print(f"Directory '{path}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
def generate_name(prefix, file_type): #genereates the name for our images and captures
    filename = f"{prefix}-{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.{file_type}"
    return filename
def main():
    parser = argparse.ArgumentParser(description ='Create a Grid World')
    parser.add_argument('--x_size', type=int , default=5,  required=False ,help='The size of the grid in the X direction' )
    parser.add_argument('--y_size', type=int , default=5,  required=False ,help='The size of the grid in the Y direction' )
    parser.add_argument('--coverage', type=float , default=0.1,  required=False ,help='What percent of the grid will be covered with obstacles' )
    parser.add_argument('--square_size', type=int , default=1,  required=False ,help='How large each square in an obstacle will be' )
    
    args = parser.parse_args()
    # hero = 
    graph_generator = generate_graph(args.x_size, args.y_size, args.coverage, args.square_size)
    map, shapes = graph_generator.make_grid()
    # wrld = world(args.x_size,args.y_size, args.coverage, args.square_size, graph_generator)
    # plt = wrld.make_starting_world(start = [0,0], goal = [5,5])
    # plt.show()


if __name__ == "__main__":
    main()