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
GOLD = (255, 215, 0)
OBSTACLE = 1
HERO = 2
ENEMY = 3
DEBRIS = 1
GOAL = 4
PATH = 7
debug = True

class game_run:
    def __init__(self, graph_generator, window_size = 1080):
        self.grid_map = None  # Store the grid map

        # print(self.TILE_SIZE)
        self.graph_generator = graph_generator
        self.delay = 500  #delay between each tick
        # self.start = start
        # self.goal = goal
        self.window_size = window_size
        self.goal = None
        self.window_height = None
        self.window_width = None
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
        pygame.draw.circle(self.screen, char.color, (x_center, y_center), self.TILE_SIZE / 2)

    def display_screen(self,status):
        win_path = "images/win.png"
        lose_path = "images/lose.png"
        images = {'win'  : (win_path, GOLD),
                  'lose' : (lose_path, RED)
                  }
        image_path, color = images[status]
        image = pygame.image.load(image_path).convert()
        width, height = image.get_width(), image.get_height()
        top_left_center_width = (self.window_width/2) - width/2
        top_left_center_height = (self.window_height/2) - height/2

        self.screen.fill(color)
        # self.screen = pygame.display.set_mode((width, height))
        self.screen.blit(image, (top_left_center_width,top_left_center_height))

    def show_path(self, path):
        path_grid = np.copy(self.grid_map)
        for i in range(len(path)):
            path_grid[int(path[i][0]), int(path[i][1])] = PATH

        self.debug_print("Path in the grid world", path_grid)
    def seperate_print(self, coord, character):
     
        seperate_grid = np.copy(self.grid_map)
        seperate_grid[coord[0], coord[1]] = character
        self.debug_print("Test Map Printing", seperate_grid)

    @staticmethod
    def debug_print(reason, printey):
        if debug:
            print(f"{reason}:\n {printey}")
    def run(self):
        invalid_hero_positions = [1, 3 , 4]
        invalid_enemy_positions = [1,2,3,4]
        num_enemies = 5
        num_wins = 0 #debug variable
        running = True #controls when the game stops
        num_init_path_tries = 0 #number of tries to find a valid world
        tick = 0 #keeps track of the game ticks

        self.grid_map = self.graph_generator.make_grid()  ##create the grid based map and initlize start and end locations
        hero_start, goal = self.graph_generator.start_and_goal(self.grid_map, invalid_hero_positions)
        self.grid_map[goal[0], goal[1]] = GOAL  
        hero = characters.hero(hero_start)  ##create the hero character with a start location
        self.grid_map = hero.move_character(hero_start, self.grid_map, HERO)
        self.debug_print("Heros position", hero.position)
        self.grid_map[hero.position[0], hero.position[1]] = HERO
        ##i need to make it so that the initialziion of a character updates the map
        enemy_list = [None] * num_enemies
        for i in range(num_enemies):
            temp_enemy_start, _ = self.graph_generator.start_and_goal(self.grid_map, invalid_enemy_positions)
            enemy = characters.enemy(temp_enemy_start)
            self.grid_map, enemy.status = enemy.move_character(temp_enemy_start, self.grid_map, ENEMY)
            enemy_list[i] = enemy
        while hero.path == None:   ##check if the map, start and goal positions can create a valid path so the game always at least tries to start
            if num_init_path_tries > 10:
                self.grid_map = self.graph_generator.make_grid()
                hero_start, goal = self.graph_generator.start_and_and_goal(self.grid_map)
            hero.path_finding(hero.position, goal, self.grid_map)
            if hero.path == None:
                hero_start, self.goal = self.graph_generator.start_and_goal(self.grid_map)
            num_init_path_tries += 1

        self.start_game(self.grid_map)
        self.debug_print("Grid map at the start", self.grid_map)
        while running:  ##infinite loop while running
            self.goal = goal
            if hero.position != goal:  ##if the hero has not reached the goal, find a path to the goal
                hero.path = None  ##clear the path before each search idk why
                tick = 1 #reset the tick counter each time we create a path
                hero.path_finding(hero.position, goal, self.grid_map) #I need to figure out why the path doesnt avoid enemies they should be ignored
                for enemy in enemy_list:
        
                    if enemy.status == 'alive':
                        enemy.path = None
                        enemy.path_finding(enemy.position, self.grid_map, hero.position)
            if hero.path == None:  ##if there is no valid path that can be found, the hero loses
                # running = False
                print("The hero lost!")
                self.display_screen('lose')
                # break
            else:
                self.screen.fill(WHITE) ##set the background
                self.draw_grid()        ##draw the base grid with obstacles
                
                if tick < len(hero.path):  #a check to make sure we dont out of bounds the path
                    self.grid_map = hero.move_character(hero.path[tick], self.grid_map, HERO)  #move the character to a new positon, and update the map and its position with that
                    pygame.time.wait(self.delay)
                    for enemy in enemy_list:
                        if enemy.path == None:
                            enemy.status = 'destroyed'
                            pass
                        self.grid_map, enemy.status = enemy.move_character(enemy.path[tick], self.grid_map, ENEMY)
                    tick += 1       #I think I can get rid of this now
                    

                self.draw_character(hero)   ##place the character on the grid
                for enemy in enemy_list:
                    self.draw_character(enemy)
                
                if hero.position == self.goal:  ##check if the game is over and the hero won
                    if debug != True:       ##in normal running, we stop running, print on the terminal the games won, and hopefulyl display a winning screen
                        # running = False
                        print("The hero won!")
                        self.display_screen('win')
                    else:                   ##debug does all that but does not kill the game
                        self.display_screen('win')
                        if num_wins < 1:
                            print("The hero won!")
                            # num_wins += 1
                            
            pygame.display.flip()
            pygame.time.wait(self.delay) #makes the game wait to do the next step
        pygame.quit()  #quic the game once we exit


def main():
    # map_array = [  Basic map for debugging
    # [0, 0, 0, 0],
    # [0, 1, 1, 0],
    # [0, 1, 1, 0],
    # [0, 0, 0, 0]
    # ]
    # start = (0,0)
    # goal = (3,3)
    parser = argparse.ArgumentParser(description ='Create a Grid World')
    parser.add_argument('--x_size', type=int , default=100,  required=False ,help='The size of the grid in the X direction' )
    parser.add_argument('--y_size', type=int , default=100,  required=False ,help='The size of the grid in the Y direction' )
    parser.add_argument('--coverage', type=float , default=0.1,  required=False ,help='What percent of the grid will be covered with obstacles' )
    parser.add_argument('--square_size', type=int , default=1,  required=False ,help='How large each square in an obstacle will be' )
    args = parser.parse_args()
    graph_generator = grid.generate_graph(args.x_size, args.y_size, args.coverage, args.square_size)
    # map_array,start, goal = graph_generator.make_grid()

    # print(map_array)
    
    game = game_run(graph_generator)
    game.run()
    
if __name__ == "__main__":
    main()