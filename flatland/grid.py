import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib
from random import randrange, choice
import random
from dataclasses import dataclass
import argparse
import matplotlib.animation as animation
from itertools import combinations
import cv2
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
        self.array = np.zeros((self.xlim, self.ylim), dtype=int) 
        self.corner_array = np.zeros((self.xlim+1, self.ylim+1), dtype=int)

    def make_grid(self):
        """Generates the array and size of the obstacle course, plots the course
        """
        num_shapes = int((self.coverage * ((self.xlim) * (self.ylim)) / (self.square_size ** 2))/4)+1
        # num_shapes = 2
        print(f"The number of shapes is {num_shapes}")
        for _ in range(num_shapes):
            self.create_shape()
        # self.generate_corner_graph()
        # start, goal = self.start_and_goal()
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
    def generate_corner_graph(self):

        for i in range(self.xlim):
            for j in range(self.ylim):
                if self.array[i][j] == 1:
                    self.corner_array[i][j] = 1
                    self.corner_array[i+1][j] = 1
                    self.corner_array[i][j+1] = 1
                    self.corner_array[i+1][j+1] = 1
        return self.corner_array

    def find_obstacle_edges(self):
        self.generate_corner_graph #make sure we actualyl find the corners first lmao
        all_edges = []
        corner_array_uint8 = self.corner_array.astype(np.uint8)
        contours, hierarchy = cv2.findContours(corner_array_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for i, contour in enumerate(contours):
            contour_edges = []  # Edges for the current contour
            contour = contour[:, 0, :]  # Reshape to (x, y)
            num_points = len(contour)

            for j in range(num_points):
                pt0 = tuple(contour[j])
                pt1 = tuple(contour[(j + 1) % num_points])
                contour_edges.append([tuple([int(pt0[0]), int(pt0[1])]), tuple([int(pt1[0]), int(pt1[1])])])
            all_edges.append(contour_edges)
        return all_edges

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
            if not self.is_obstacle(start_x, start_y, grid) and not self.is_obstacle(goal_x, goal_y, grid):
                return (int(start_y), int(start_x)), (int(goal_y), int(goal_x))
            print("Recalculating goals")
    @staticmethod
    def is_obstacle(row, col, map_world):
        return map_world[row][col] == 1
   




        


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