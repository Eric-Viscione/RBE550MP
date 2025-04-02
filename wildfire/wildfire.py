import pygame
import grid
import argparse
import numpy as np
# import search_algorithms
# import characters
import pyautogui
import logging
import datetime
import os
logger = logging.getLogger(__name__)
#from planners import 
# Constants


# Colors
BUTTON_LIGHT = (170,170,170)
BUTTON_DARK = (100,100,100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
OBSTACLE = 1
HERO = 2
ENEMY = 3
DEBRIS = 1
GOAL = 4
PATH = 7
debug = False



class renderer:
    def __init__(self,  window_size = 1000 ):
        self.screen = None
        self.status = None
        self.window_size = window_size
        self.goal = None
        pass
    def update_screen(self, status, grid_map, characters, goal):
        self.goal = goal
        # print(status)
        if status == 'lost':
            self.display_screen(status)
        elif status == 'won':
            self.display_screen(status)
        else:
            self.draw_grid()
            if characters is not None:
                for character in characters:
                    self.draw_character(character)
                    self.draw_path(character)
    def draw_grid(self):
        font = pygame.font.SysFont("Arial", 12)  # Set font and size for the text
        self.screen.fill(WHITE) ##set the background
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

    def draw_path(self, char):
        """Draw the path of the given character based on its path plan

        Args:
            char (_type_): _description_
        """
        # print(char.path)
        # print(type(char.path))

        if char.path is not None and char.status == 'alive':
            for i in range(len(char.path)-1):
                curr_x_center = (char.path[i][1]) * self.TILE_SIZE + (self.TILE_SIZE / 2)  # For x, use column (pos[1])
                curr_y_center = char.path[i][0] * self.TILE_SIZE + (self.TILE_SIZE / 2)  # For y, use row (pos[0])
                next_x_center = (char.path[i+1][1]) * self.TILE_SIZE + (self.TILE_SIZE / 2)  # For x, use column (pos[1])
                next_y_center = char.path[i+1][0] * self.TILE_SIZE + (self.TILE_SIZE / 2)  # For y, use row (pos[0])
                pygame.draw.line(self.screen, char.color, (curr_x_center, curr_y_center), (next_x_center, next_y_center), 5)



    def draw_x(self, pos, width = 5):
        if pos is None:
            return
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
        
        
        x_center = (char.position[1]) * self.TILE_SIZE + (self.TILE_SIZE / 2)  # For x, use column (pos[1])
        y_center = char.position[0] * self.TILE_SIZE + (self.TILE_SIZE / 2)  # For y, use row (pos[0])
        pygame.draw.circle(self.screen, char.color, (x_center, y_center), self.TILE_SIZE / 2)

    def display_screen(self,status):
        # print('Showing ', status)
        win_path = "images/win.png"
        lose_path = "images/lose.png"
        images = {'won'  : (win_path, GOLD),
                  'lost' : (lose_path, RED)
                  }
        image_path, color = images[status]
        image = pygame.image.load(image_path).convert()
        width, height = image.get_width(), image.get_height()
        top_left_center_width = (self.window_width/2) - width/2
        top_left_center_height = (self.window_height/2) - height/2

        self.screen.fill(color)
        # self.screen = pygame.display.set_mode((width, height))
        self.screen.blit(image, (top_left_center_width,top_left_center_height))
    def start_game(self, grid_map):

        if grid_map is None or grid_map.size == 0:  # Check for empty grid
            raise ValueError("Grid map is empty or invalid!")
        
        self.grid_map = grid_map
        width = len(self.grid_map[0])
        height = len(self.grid_map)
        self.TILE_SIZE = int(min(self.window_size/width, self.window_size/height))

        GRID_WIDTH = len(self.grid_map[0]) * self.TILE_SIZE
        GRID_HEIGHT = len(self.grid_map) * self.TILE_SIZE
        self.window_width = GRID_WIDTH
        self.window_height = GRID_HEIGHT
        pygame.init()
        pygame.display.set_caption("Flatlands")
        self.screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
        self.clock = pygame.time.Clock()
    def draw_button(self):
        mouse = pygame.mouse.get_pos()  
        if self.window_width / 2 <= mouse[0] <= self.window_width / 2 + self.TILE_SIZE and self.window_height / 2 <= mouse[1] <= self.window_height / 2 + self.TILE_SIZE:  
            pygame.draw.rect(self.screen, BUTTON_LIGHT, [self.window_width , self.window_height , self.TILE_SIZE, self.TILE_SIZE])  
        else:  
            pygame.draw.rect(self.screen, BUTTON_DARK, [self.window_width , self.window_height , self.TILE_SIZE, self.TILE_SIZE])
class game_run:

    def __init__(self, graph_generator,renderer, tick_speed, num_enemies, statistics):
        self.graph_generator = graph_generator
        self.renderer = renderer
        self.grid_map = None  # Store the grid map        
        self.running = True
        self.hero = None

        self.goal = None
        self.status = 'running'
        self.delay = tick_speed
        self.statistics = statistics
    def world_setup(self):
        self.grid_map = self.graph_generator.make_grid()  ##create the grid based map and initlize start and end locations
    def move_characters(self):
        pass
    def run(self):
        self.world_setup()
        self.renderer.start_game(self.grid_map)
        loop_num = 0
        while self.running:  ##infinite loop while running
            
            self.move_characters()

            self.renderer.update_screen(self.status, self.grid_map, self.hero, self.goal)
                            
            pygame.display.flip()
            if loop_num == 0:
                pygame.time.wait(self.delay*10) #makes the game wait to do the next step
            else:
                pygame.time.wait(self.delay)
            if self.statistics:
                print("simulating")
                if self.status != 'running':
                    self.running = False
            loop_num += 1
        pygame.quit()
        return self.status
        # pygame.quit()  #quit the game once we exit

def create_directory(path):
        try: ##directory creation references from geeksforgeeks.com
            os.mkdir(path)
            print(f"Directory '{path}' created successfully.")
        except FileExistsError:
            print(f"Directory '{path}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{path}'.")
        except Exception as e:
            print(f"An error occurred: {e}")
def main():
    create_directory('temp')
    log_filename = f"temp/run_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO)

    parser = argparse.ArgumentParser(description ='Create a Grid World')
    parser.add_argument('--x_size', type=int , default=50,  required=False ,help='The size of the grid in the X direction' )
    parser.add_argument('--y_size', type=int , default=50,  required=False ,help='The size of the grid in the Y direction' )
    parser.add_argument('--coverage', type=float , default=0.2,  required=False ,help='What percent of the grid will be covered with obstacles' )
    parser.add_argument('--square_size', type=int , default=1,  required=False ,help='How large each square in an obstacle will be' )
    parser.add_argument('--num_enemies',type=int , default=0,  required=False ,help='Number of enemies in the world' )
    parser.add_argument('--tick_speed',type=int , default=250,  required=False ,help='Time betwen ticks in ms' )
    
    args = parser.parse_args()

    num_simualtions = 1
    num_wins = 0
    num_losses = 0
    # args.tick_speed = 1/
    for i in range(num_simualtions):
        graph_generator = grid.generate_graph(args.x_size, args.y_size, args.coverage, args.square_size)
        renderer_engine = renderer()
        game = game_run(graph_generator, renderer_engine, args.tick_speed, args.num_enemies, False)
        result = game.run()
        if result == 'lost':
            num_losses +=1
        else:
            num_wins += 1
    print(F"Wins: {num_wins}")
    print(F"Losses: {num_losses}")

    print(F"Win percentage: {int(num_wins/num_simualtions)*100}%")    
if __name__ == "__main__":
    main()





        # map_array = [  Basic map for debugging
    # [0, 0, 0, 0],
    # [0, 1, 1, 0],
    # [0, 1, 1, 0],
    # [0, 0, 0, 0]
    # ]
    # start = (0,0)
    # goal = (3,3)
