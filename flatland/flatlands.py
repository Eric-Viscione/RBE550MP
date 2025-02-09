import pygame
import grid
import argparse
import numpy as np
import search_algorithms
import characters
import pyautogui
import logging
import datetime
import os
logger = logging.getLogger(__name__)
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
    def update_screen(self, status, grid_map, hero, enemy_list, goal):
        self.goal = goal
        # print(status)
        if status == 'lost':
            self.display_screen(status)
        elif status == 'won':
            self.display_screen(status)
        else:
            self.draw_grid()
            self.draw_character(hero)
            self.draw_path(hero)
            self.draw_button()
            for enemy in enemy_list:
                self.draw_character(enemy)
                self.draw_path(enemy)
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
        self.invalid_hero_positions = invalid_hero_positions = [1,3,4]
        self.invalid_enemy_positions = invalid_enemy_positions = [1,2,3,4]
        self.num_enemies =  num_enemies
        self.enemy_list = [None] *self.num_enemies
        self.goal = None
        self.status = 'running'
        self.delay = tick_speed
        self.statistics = statistics
    def world_setup(self):
        num_init_path_tries = 0
        num_retries = 10
        self.grid_map = self.graph_generator.make_grid()  ##create the grid based map and initlize start and end locations
        hero_start, self.goal = self.graph_generator.start_and_goal(self.grid_map, self.invalid_hero_positions)
        # self.grid_map[self.goal[0], self.goal[1]] = GOAL  
        self.hero = characters.hero(hero_start)  ##create the hero character with a start location
        self.grid_map = self.hero.move_character(hero_start, self.grid_map, HERO)

        while self.hero.path == None and num_retries < 10:   ##check if the map, start and goal positions can create a valid path so the game always at least tries to start
            if num_init_path_tries > 10:
                self.grid_map = self.graph_generator.make_grid()
                hero_start, self.goal = self.graph_generator.start_and_goal(self.grid_map, self.invalid_hero_positions)
            if hero_start is not None and self.goal is not None:
                print("Trying again")
                self.hero.path_finding(self.hero.position, self.goal, self.grid_map)
                self.grid_map = self.graph_generator.make_grid()
                num_retries += 1
            if self.hero.path == None:
                hero_start, self.goal = self.graph_generator.start_and_goal(self.grid_map, self.invalid_hero_positions)
            num_init_path_tries += 1


        for i in range(self.num_enemies):
            temp_enemy_start, _ = self.graph_generator.start_and_goal(self.grid_map, self.invalid_enemy_positions)
            enemy = characters.enemy(temp_enemy_start)
            self.grid_map, enemy.status = enemy.move_character(temp_enemy_start, self.grid_map, ENEMY)
            self.enemy_list[i] = enemy
    def character_paths(self):
        if self.hero.position != self.goal:  ##if the hero has not reached the goal, find a path to the goal
            self.hero.path = None  ##clear the path before each search idk why
            self.hero.path_finding(self.hero.position, self.goal, self.grid_map) #I need to figure out why the path doesnt avoid enemies they should be ignored

            for enemy in self.enemy_list:
                if enemy.status == 'alive':
                    enemy.path = None
                    enemy.path_finding(enemy.position, self.grid_map, self.hero.position)

    def move_characters(self):
        logging.info(self.hero.path)
        if self.hero.path is None:
            self.status = 'lost'
            # print("LOSER")

        elif self.hero.position == self.goal:
            self.status = 'won'
        else:
            self.status = 'running'
            if len(self.hero.path) >= 2:
                self.grid_map = self.hero.move_character(self.hero.path[1], self.grid_map, HERO)  #move the character to a new positon, and update the map and its position with that
            for enemy in self.enemy_list:
                if enemy.path == None:
                    enemy.status = 'destroyed'
                    self.grid_map, enemy.status = enemy.move_character(enemy.position, self.grid_map, ENEMY)
                    pass
                else:
                    if len(enemy.path) >= 2:
                        self.grid_map, enemy.status = enemy.move_character(enemy.path[1], self.grid_map, ENEMY)
        # print(self.status)


    def run(self):
        num_wins = 0 #debug variable
         #number of tries to find a valid world
        tick = 1 #keeps track of the game ticks
        self.world_setup()
        self.renderer.start_game(self.grid_map)
        loop_num = 0
        while self.running:  ##infinite loop while running
            
            self.character_paths()
            self.move_characters()
            # if self.status == 'lost':
            # elif hero.position
            self.renderer.update_screen(self.status, self.grid_map, self.hero, self.enemy_list, self.goal)
                            
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
    # map_array = [  Basic map for debugging
    # [0, 0, 0, 0],
    # [0, 1, 1, 0],
    # [0, 1, 1, 0],
    # [0, 0, 0, 0]
    # ]
    # start = (0,0)
    # goal = (3,3)
    parser = argparse.ArgumentParser(description ='Create a Grid World')
    parser.add_argument('--x_size', type=int , default=50,  required=False ,help='The size of the grid in the X direction' )
    parser.add_argument('--y_size', type=int , default=50,  required=False ,help='The size of the grid in the Y direction' )
    parser.add_argument('--coverage', type=float , default=0.2,  required=False ,help='What percent of the grid will be covered with obstacles' )
    parser.add_argument('--square_size', type=int , default=1,  required=False ,help='How large each square in an obstacle will be' )
    parser.add_argument('--num_enemies',type=int , default=10,  required=False ,help='Number of enemies in the world' )
    parser.add_argument('--tick_speed',type=int , default=250,  required=False ,help='Time betwen ticks in ms' )
    
    args = parser.parse_args()

    # map_array,start, goal = graph_generator.make_grid()

    # print(map_array)
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