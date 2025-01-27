import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib
from random import randrange, choice
import random
from dataclasses import dataclass
import argparse
import matplotlib.animation as animation

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

class agent:
    def __init__(self, color):
        self.color = color
        self.current_square = None
        





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
        
    def make_grid(self):
        """Generates the array and size of the obstacle course, plots the course
        """
        num_shapes = int((self.coverage * ((self.xlim) * (self.ylim)) / (self.square_size ** 2))/4)+1
        print(f"The number of shapes is {num_shapes}")
        for _ in range(num_shapes):
            self.create_shape()
        print(self.array)
        return self.array
        # title = f"{self.xlim} X {self.ylim} Grid with {self.coverage*100}% Covereage"
        # self.visualize_grid(title)
        # input()
    def create_shape(self):
        """Randomly seeds a shape that has and area of self.obstacle_size 
            The squares grow from the inital seed in a random direction
            The shape is stored by its starting corner in the array of the entire map
        """
        open_x, open_y = np.where(self.array == 0)
        self.x_start = random.choice(open_x)
        self.y_start = random.choice(open_y)
        self.array[self.y_start, self.x_start] = 1
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
        #generate all random numbers 0-obstacle_size and remove theinvalid entry that would cause double backing
        invalid_dir = None
        if check_dir is not None:    
            invalid_dir_check = next((entry for entry in mapping if entry.value == check_dir))
            if invalid_dir_check:
                invalid_dir = invalid_dir_check.value

        valid_dirs = list(range(self.obstacle_size))
        if invalid_dir is not None and invalid_dir in valid_dirs:
            valid_dirs.remove(invalid_dir)  # Only remove if check_dir is in valid_dirs   
        # print(f"Valid Directions are {valid_dirs}")
        rand_num = choice(valid_dirs)
        # print(f"random number is {rand_num}")
        direction = next((entry for entry in mapping if entry.value == rand_num))         #update the x_start and y_Start
        if direction:
            self.x_start = self.x_start + direction.x
            self.y_start = self.y_start + direction.y
    
            self.prev_dir = direction.inverse
    def generate_corner_graph(self):
        
class world:
    def __init__(self, xlim, ylim, coverage, square_size, graph_generator):
        self.xlim = xlim
        self.ylim = ylim
        self.coverage = coverage
        self.fig = None
        self.square_size = square_size
        self.x_start = 0
        self.y_start = 0
        self.obstacle_size = 4
        self.prev_dir = 0
        self.array = np.zeros((self.xlim, self.ylim), dtype=int)
        self.graph_generator = graph_generator
    def plot_setup(self, title):
        """Sets up the plot, adding its grid, title and limits

        Args:
            title (string): Title of the plot

        Returns:
            ay: object of the figure that holds the formatting data
        """
        self.fig, ay = plt.subplots()
        ay.grid(True)
        ay.set_xlim([0, self.xlim])
        ay.set_ylim([0, self.ylim])
        ay.set_xticks(range(0, self.xlim + 1, 1))
        ay.set_yticks(range(0, self.ylim + 1, 1))
        ay.set_title(title)
        return ay
    
    def visualize_grid(self, title):
        """Adds rectangles to the course visualization based on the array
           Also adds scatter points to each start point

        Args:
            title (string): Title of the plot
        """
        ay = self.plot_setup(title)
        for i in range(self.xlim):
            for j in range(self.ylim):
                if self.array[i][j] == 1:
                    rect = matplotlib.patches.Rectangle((i, j), self.square_size, self.square_size, 
                                  edgecolor='black', facecolor='blue', alpha=0.5)  ##to do seperate the graphing into a more portable class so I can generate the grid, pass that around and then plot;
                    print(f'Rectangle starting at {i}, {j}')
                    ay.add_patch(rect)
        x_indices, y_indices = np.where(self.array == 1)
        plt.scatter(x_indices+0.5, y_indices+0.5, s=25)
        plt.show()
    def make_starting_world(self):
        """Generates the array and size of the obstacle course, plots the course
        """
        self.array = self.graph_generator.make_grid()
        title = f"{self.xlim} X {self.ylim} Grid with {self.coverage*100}% Covereage"
        self.visualize_grid(title)
        input()



        


def main():
    parser = argparse.ArgumentParser(description ='Create a Grid World')
    parser.add_argument('--x_size', type=int , default=100,  required=False ,help='The size of the grid in the X direction' )
    parser.add_argument('--y_size', type=int , default=100,  required=False ,help='The size of the grid in the Y direction' )
    parser.add_argument('--coverage', type=float , default=0.1,  required=False ,help='What percent of the grid will be covered with obstacles' )
    parser.add_argument('--square_size', type=int , default=1,  required=False ,help='How large each square in an obstacle will be' )
    
    args = parser.parse_args()
    graph_generator = generate_graph(args.x_size, args.y_size, args.coverage, args.square_size)
    wrld = world(args.x_size,args.y_size, args.coverage, args.square_size, graph_generator)
    wrld.make_starting_world()


if __name__ == "__main__":
    main()