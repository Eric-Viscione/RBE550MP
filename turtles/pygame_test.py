import pygame
import grid
import argparse
import numpy as np
import search_algorithms
import characters
import pyautogui
# Constants


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

debug = False

class game_run:
    def __init__(self, grid_map, start, goal , window_size = 1080):
        self.grid_map = grid_map  # Store the grid map
        width = len(self.grid_map[0])
        height = len(self.grid_map)
        self.TILE_SIZE = int(min(window_size/width, window_size/height))
        print(self.TILE_SIZE)

        
        self.GRID_WIDTH = len(self.grid_map[0]) * self.TILE_SIZE
        self.GRID_HEIGHT = len(self.grid_map) * self.TILE_SIZE

        self.delay = 500
        self.start = start
        self.goal = goal

        pygame.init()
        pygame.display.set_caption("Binary Grid Map")
        self.screen = pygame.display.set_mode((self.GRID_WIDTH, self.GRID_HEIGHT))
        self.clock = pygame.time.Clock()
    def draw_grid(self):
        font = pygame.font.SysFont("Arial", 12)  # Set font and size for the text

        """Draw the grid based on binary data."""
        for row in range(len(self.grid_map)):
            for col in range(len(self.grid_map[row])):
                rect = pygame.Rect(col * self.TILE_SIZE, row * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                color = BLACK if self.grid_map[row][col] == 1 else WHITE
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)  # Grid lines
                if debug:
                    text = font.render(f"({row},{col})", True, (0, 0, 0)) 
                    text_rect = text.get_rect(center=rect.center)  
                    self.screen.blit(text, text_rect)  
        # self.draw_x(self.start)
        self.draw_x(self.goal)

    def draw_x(self, pos, width = 5):
        #the center is the grid spot we want to put it in
        #Get the top left of the shape and the bottom right
        #get the top right and bottom left
        # print("Position is",pos)
        x = (pos[1]+1) * self.TILE_SIZE
        y = (pos[0]) * self.TILE_SIZE
        # print(f"The x and y are {x}, {y}")
        TL = (x - (self.TILE_SIZE), y + (self.TILE_SIZE))
        TR = (x , y + (self.TILE_SIZE))
        BL = (x - (self.TILE_SIZE), y)
        BR = (x , y)

        # Draw the two diagonal lines that make up the X
        pygame.draw.line(self.screen, BLUE, TL, BR, width)
        pygame.draw.line(self.screen, BLUE, TR, BL, width)
        pygame.draw.circle(self.screen, BLUE, (x - (self.TILE_SIZE/2) , y + (self.TILE_SIZE/2)), self.TILE_SIZE/8)

    def draw_character(self, char):
        # print("Characters Position", char.position)
        scale_factor = self.TILE_SIZE
        x_center = (char.position[1]) * scale_factor + (self.TILE_SIZE / 2)  # For x, use column (pos[1])
        y_center = char.position[0] * scale_factor + (self.TILE_SIZE / 2)  # For y, use row (pos[0])
        pygame.draw.circle(self.screen, GREEN, (x_center, y_center), self.TILE_SIZE / 2)



    def run(self):
        
        running = True
        hero = characters.hero(self.start, self.grid_map, self.goal, debug)
        tick = 0
        hero.path_finding()
        if hero.path == None:
            self.start, self.goal = grid.start_and_goal()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.screen.fill(WHITE)
            self.draw_grid()
            
            if tick < len(hero.path):
                hero.move_character(hero.path[tick])
                tick += 1
                pygame.time.wait(self.delay)
            else:
                pygame.time.wait(self.delay)

            self.draw_character(hero)
            pygame.display.flip()
            
            # if hero.position == self.goal:
            #     print("The hero won!")
                # running = False
            self.clock.tick(60)
        pygame.quit()


def main():
    parser = argparse.ArgumentParser(description ='Create a Grid World')
    parser.add_argument('--x_size', type=int , default=50,  required=False ,help='The size of the grid in the X direction' )
    parser.add_argument('--y_size', type=int , default=50,  required=False ,help='The size of the grid in the Y direction' )
    parser.add_argument('--coverage', type=float , default=0.1,  required=False ,help='What percent of the grid will be covered with obstacles' )
    parser.add_argument('--square_size', type=int , default=1,  required=False ,help='How large each square in an obstacle will be' )
    args = parser.parse_args()
    graph_generator = grid.generate_graph(args.x_size, args.y_size, args.coverage, args.square_size)
    map_array,start, goal = graph_generator.make_grid()
    # map_array = [
    # [0, 0, 0, 0],
    # [0, 1, 1, 0],
    # [0, 1, 1, 0],
    # [0, 0, 0, 0]
    # ]
    # start = (0,0)
    # goal = (3,3)
    print(map_array)
    # map_array = map_array.tolist()
    
    game = game_run(map_array, start, goal)
    game.run()
    
if __name__ == "__main__":
    main()