import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib
from random import randrange



class world:
    def __init__(self, xlim, ylim, coverage, square_size):
        self.xlim = xlim
        self.ylim = ylim
        self.coverage = coverage
        self.fig = None
        self.square_size = square_size
    def setup(self):
        self.fig, ax = plt.subplots()
        ax.set_xlim([-self.xlim, self.xlim])
        ax.set_ylim([-self.ylim, self.ylim])
        ax.set_aspect('equal')
        return ax
    
    def shape(self, ax):
        x_start = randrange(self.xlim*2)-self.xlim
        print(x_start)
        
        y_start = randrange(self.ylim*2)-self.ylim
        print(y_start)
        rect = matplotlib.patches.Rectangle((x_start, y_start), self.square_size, self.square_size, 
                                  edgecolor='black', facecolor='blue', alpha=0.5)        
        ax.add_patch(rect)

    def make_grid(self):
        ax = self.setup()
        num_shapes = int(self.coverage * ((2 * self.xlim) * (2 * self.ylim)) / (self.square_size ** 2))

        for _ in range(num_shapes):
            self.shape(ax)
        ax.grid(True)
        plt.show()
        


def main():
    wrld = world(10, 10, 0.1, 1)
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