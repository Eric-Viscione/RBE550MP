import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib
from random import randrange, choice
from dataclasses import dataclass
import argparse
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



class world:
    def __init__(self, xlim, ylim, coverage, square_size):
        self.xlim = xlim
        self.ylim = ylim
        self.coverage = coverage
        self.fig = None
        self.square_size = square_size
        self.x_start = 0
        self.y_start = 0
        self.obstacle_size = 4
        self.prev_dir = 0
        self.array = np.zeros((self.xlim, self.ylim), dtype=int) #The array is stored flipped from what is plotted cant figure out how to fix that
    def setup(self):
        self.fig, ax = plt.subplots()
        ax.set_xlim([0, self.xlim])
        ax.set_ylim([0, self.ylim])
        ax.set_aspect('equal')
        return ax
    
    def shape(self, ax):
        self.x_start = randrange(self.xlim-1)
        # print(self.x_start)
        
        self.y_start = randrange(self.ylim-1)
        # print(self.y_start)
        if self.array[self.x_start, self.y_start] == 1:# Skip if the starting position is already occupied
            return  
        rect = matplotlib.patches.Rectangle((self.x_start, self.y_start), self.square_size, self.square_size, #generate the first rectangle
                                  edgecolor='black', facecolor='blue', alpha=0.5)
        self.array[self.y_start, self.x_start] = 1
        ax.add_patch(rect)
        self.prev_dir = None
        for i in range(3):         #randomly increment in one direction frrom the previous rectangle, adding it to the graph. when you get to 3 new rectangles stop       
            self.choose_dir(self.prev_dir)
            if self.x_start >= self.xlim:
                self.x_start = self.xlim-1
            if self.y_start >= self.ylim:
                self.y_start = self.ylim-1
            rect = matplotlib.patches.Rectangle((self.x_start, self.y_start), self.square_size, self.square_size, #generate the first rectangle
                                  edgecolor='black', facecolor='blue', alpha=0.5)
            self.array[self.y_start, self.x_start] = 1

            ax.add_patch(rect)

            


        
    def choose_dir(self, check_dir):
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

    def make_grid(self):
        ax = self.setup()
        num_shapes = int((self.coverage * ((self.xlim) * (self.ylim)) / (self.square_size ** 2))/4)+1

        print(f"The number of shapes is {num_shapes}")
        # num_shapes = 5
        for _ in range(num_shapes):
            self.shape(ax)
        print(self.array)
        ax.grid(True)
        # plt.show()
        y_indices, x_indices = np.where(self.array == 1)
        plt.scatter(x_indices, y_indices, s=2)
        plt.title(f"{self.xlim} X {self.ylim} Grid with {self.coverage*100}% Covereage")
        plt.savefig(f"{self.xlim}_X_{self.ylim}_Grid_with_{self.coverage*100}_Percent_Covereage.png")
        plt.show()



        


def main():
    parser = argparse.ArgumentParser(description ='Create a Grid World')
    parser.add_argument('--x_size', type=int , default=100,  required=False ,help='The size of the grid in the X direction' )
    parser.add_argument('--y_size', type=int , default=100,  required=False ,help='The size of the grid in the Y direction' )
    parser.add_argument('--coverage', type=float , default=0.1,  required=False ,help='What percent of the grid will be covered with obstacles' )
    parser.add_argument('--square_size', type=int , default=1,  required=False ,help='How large each square in an obstacle will be' )
    
    args = parser.parse_args()
    
    wrld = world(args.x_size,args.y_size, args.coverage, args.square_size)
    wrld.make_grid()


if __name__ == "__main__":
    main()
# fig = plt.figure() 
# ax = fig.add_subplot(111) 
# rect1 = matplotlib.patches.Rectangle((-1, -5), 
#                                      1, 5, 
#                                      color ='green') 
# ax.add_patch(rect1)
# plt.xlim([-10, 10])
# plt.ylim([-10, 10])
# plt.grid()
# plt.show() 