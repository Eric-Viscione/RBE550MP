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
    
    def visualize_grid(self, title, corner_array):
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
                    # print(f'Rectangle starting at {i}, {j}')
                    ay.add_patch(rect)
        x_indices_starts, y_indices_starts = np.where(self.array == 1)
        plt.scatter(x_indices_starts+0.5, y_indices_starts+0.5, s=25, c='purple')
        return plt
    def make_starting_world(self, start, goal):
        """Generates the array and size of the obstacle course, plots the course
        """
        self.array = self.graph_generator.make_grid()
        corner_array = self.graph_generator.generate_corner_graph()
        title = f"{self.xlim} X {self.ylim} Grid with {self.coverage*100}% Covereage"
        plt = self.visualize_grid(title, corner_array)
        x_corners, y_corners = np.where(corner_array == 1)
        plt.scatter(x_corners, y_corners, s=25, c='blue')
        plt.scatter(start[0], start[1], s=100, c='green')
        plt.scatter(goal[0], goal[1], s=100, c='red')
       
        # plt.show()
        
        return plt