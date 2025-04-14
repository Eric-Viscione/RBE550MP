import pygame
import grid
import argparse
import numpy as np
# import search_algorithms
# import characters
from prm_planner import prm_planner, generate_continuous_path
import logging
import datetime
import os
logger = logging.getLogger(__name__)
from search_algorithms import a_star_search
from random import choice
import math
import time

#from planners import 
# Constants

prm_times = []
astar_times = []
# Colors
BUTTON_LIGHT = (170,170,170)
BUTTON_DARK = (100,100,100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)

OBSTACLE = 1
FIRE = 2
EXTINGUISHED = 3
FREE = 0
TILE_SIZE = 20
BURNED = 4
debug = False

class Character:
    def __init__(self, position, color, name, path=None):
        self.position = position  # grid position like (row, col)
        self.pixel_position = self.grid_to_pixel(position)  # smooth pos
        self.color = color
        self.path = path
        self.name = name
        self.ticks_spot = 0
        self.at_target = False
        self.speed = 2.5  # pixels per tick
        self.next_target = None
    def grid_to_pixel(self, pos):
        row, col = pos
        return (col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2)

    def pixel_to_grid(self, pixel_pos):
        x, y = pixel_pos
        col = int(x // TILE_SIZE)
        row = int(y // TILE_SIZE)
        return (row, col)
def plot_planner_times(prm_times, astar_times):
    total_prm = sum(prm_times)
    total_astar = sum(astar_times)

    planners = ['PRM', 'A*']
    times = [total_prm, total_astar]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(planners, times)

    # Add labels on top of bars
    for bar, t in zip(bars, times):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.01, f"{t:.3f}s", ha='center', va='bottom')

    plt.title("Total Time Spent in Each Planner")
    plt.ylabel("Time (seconds)")
    plt.tight_layout()
    plt.show()
class renderer:
    def __init__(self,  window_size = 1000 ):
        self.screen = None
        self.status = None
        self.window_size = window_size
        self.goal = None
        pass
    def update_screen(self, status, grid_map, characters, goal, prm_data=None):
        self.grid_map = grid_map 
        self.goal = goal
       
        self.screen.fill(WHITE) ##set the background
        for row in range(len(self.grid_map)):
            for col in range(len(self.grid_map[row])):
                rect = pygame.Rect(col * self.TILE_SIZE, row * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                color = BLACK if self.grid_map[row][col] == 1 else WHITE
                if self.grid_map[row][col] == FIRE:
                    color = RED
                if self.grid_map[row][col] == EXTINGUISHED:
                    color = BLUE
                if self.grid_map[row][col] == BURNED:
                    color = BROWN
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)  # Grid lines
                # if debug:
                #     text = font.render(f"({row},{col})", True, (0, 0, 0)) 
                #     text_rect = text.get_rect(center=rect.center)  
                #     self.screen.blit(text, text_rect)  
        # self.draw_x(self.start)
        self.draw_x(self.goal)
        for character in characters:
            self.draw_character(character)


    
    
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
        x_center, y_center = char.pixel_position
        pygame.draw.circle(self.screen, char.color, (int(x_center), int(y_center)), self.TILE_SIZE // 2)


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
        # self.TILE_SIZE = int(min(self.window_size/width, self.window_size/height))
        self.TILE_SIZE = TILE_SIZE
        # print(f"Tilesize {self.TILE_SIZE}")
        GRID_WIDTH = len(self.grid_map[0]) * self.TILE_SIZE
        GRID_HEIGHT = len(self.grid_map) * self.TILE_SIZE
        self.window_width = GRID_WIDTH
        self.window_height = GRID_HEIGHT
        # pygame.init()
        pygame.display.set_caption("Flatlands")
        self.screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
        self.clock = pygame.time.Clock()

class game_run:

    def __init__(self, graph_generator,renderer, tick_speed, num_enemies, statistics):
        self.graph_generator = graph_generator
        self.renderer = renderer
        self.grid_map = None  # Store the grid map        
        self.running = True
        self.hero = None

        self.goal = None
        self.status = 'running'
        self.delay = 1
        self.statistics = statistics
        self.prm_data = None
        self.tick_count = 0
        self.fire_timers = {}
        self.clock = pygame.time.Clock()
    def world_setup(self):
        self.grid_map = self.graph_generator.make_grid()  ##create the grid based map and initlize start and end locations
        self.start = self.graph_generator.choose_open_spot()
        self.goal = self.graph_generator.choose_open_spot()
        self.firefighter = Character(self.graph_generator.choose_open_spot(), BLUE,"firefighter",  None)
        self.wombus = Character(self.graph_generator.choose_open_spot(), RED, 'wombus' ,None )
        self.characters = [self.firefighter, self.wombus]


    def move_characters(self):
        for char in self.characters:
            if not char.path or len(char.path) == 0:
                # Clear path and mark as at target when we've completed the path
                if char.path is not None:  # Not None but empty
                    # char.path = None
                    char.at_target = True
                continue

            # First point in path is our current target
            next_grid = char.path[0]
            if not hasattr(char, "target_pixel") or char.target_pixel is None:
                char.target_pixel = char.grid_to_pixel(next_grid)
            
            # Compute direction vector
            curr_x, curr_y = char.pixel_position
            target_x, target_y = char.target_pixel
            dx = target_x - curr_x
            dy = target_y - curr_y
            dist = math.hypot(dx, dy)

            if dist < char.speed:
                # Snap to the target and update to next path point
                char.pixel_position = (target_x, target_y)
                char.position = char.pixel_to_grid(char.pixel_position)
                
                # Remove the point we just reached
                char.path.pop(0)

                if char.path:
                    # Move to next point
                    next_grid = char.path[0]
                    char.target_pixel = char.grid_to_pixel(next_grid)
                else:
                    # Path complete
                    char.target_pixel = None
                    char.at_target = True
            else:
                # Move smoothly toward the target
                ratio = char.speed / dist
                new_x = curr_x + dx * ratio
                new_y = curr_y + dy * ratio
                char.pixel_position = (new_x, new_y)
    def find_designated_spot(self, grid, value):
        rows, cols = np.where(grid == value)
        if rows.size == 0:
            return None
        spot_pairs = list(zip(rows, cols))
        rand_spot = choice(spot_pairs)
        # print(rand_spot)
        return rand_spot
    def find_nearest_navigable_spot(self, grid, value):
        spot = self.find_designated_spot(grid, value)
        # print(spot)
        if spot is None:
            return None, None
        radius = 1
        x, y = spot
        x_min = max(0, x - radius)
        x_max = min(grid.shape[0], x + radius + 1)
        y_min = max(0, y - radius)
        y_max = min(grid.shape[1], y + radius + 1)
        free_indices = np.where(grid[x_min:x_max, y_min:y_max] == 0)
        
        # Check if there are any free cells in the subgrid
        if free_indices[0].size == 0:
            return None, None

        # Convert free_indices into a list of (row, col) pairs
        free_coords = list(zip(free_indices[0], free_indices[1]))
        # Adjust coordinates back to full grid indices
        free_coords = [(i + x_min, j + y_min) for i, j in free_coords]
        
        return choice(free_coords), spot
    def sanitize_grid_for_planning(self,grid):
        # Replace FIRE and EXTINGUISHED with FREE
        sanitized = grid.copy()
        sanitized[sanitized == FIRE] = 1
        sanitized[sanitized == EXTINGUISHED] = 1
        sanitized[sanitized == BURNED] = 1
        return sanitized
    def distance(self,point1, point2):
        x0,y0 = point1
        x1,y1 = point2
        
        return math.sqrt(((x1 - x0) ** 2) + ((y1 - y0) ** 2))
    def path_characters(self):
        grid = self.sanitize_grid_for_planning(np.array(self.grid_map))
     


        if self.wombus.path is None:
            if self.wombus.at_target:
            # Reset at_target when we're finding a new path
                self.wombus.at_target = False
            
            spot, self.wombus.next_target = self.find_nearest_navigable_spot(grid, OBSTACLE)

            if spot:
                # print("Finding a new target")
                start_time = time.time()
                path = a_star_search(self.wombus.position, spot, grid)
                if path is None:
                    print("Wombus cant find where to go no more fires")
                    self.running = False
                self.wombus.path = path
                end_time = time.time()
                astar_times.append(end_time-start_time)
                self.wombus.ticks_spot = 0

        else:
            if self.wombus.at_target:
                self.wombus.ticks_spot += 1
                if self.wombus.ticks_spot > 10:
                # self.wombus.position = self.wombus.path[0]
                    # print(self.wombus.next_target)
                    # print(self.wombus.position)

                    self.grid_map[self.wombus.next_target[0], self.wombus.next_target[1]] = FIRE
                    current_tick = self.tick_count 
                    self.fire_timers[(self.wombus.next_target[0], self.wombus.next_target[1])] = current_tick
                    self.wombus.path = None
                    self.wombus.next_target = None
                    self.wombus.ticks_spot = 0
                    # print("Wombus started a fire")

        fire_locations = np.argwhere(np.array(self.grid_map) == FIRE)
        if fire_locations.size > 0 and self.firefighter.path is None:
            firefighter_start = self.firefighter.position

            fire_spots = [tuple(row) for row in fire_locations]
            fire_goal = min(fire_spots, key=lambda p: self.distance(firefighter_start, p))
            self.firefighter.next_target = fire_goal
            start_time = time.time()
            sparse_path, nodes, edges = prm_planner(grid, firefighter_start, fire_goal, num_samples=1000, connection_radius=5)
            self.firefighter.path = sparse_path
            # show_prm_path(grid, nodes, edges, sparse_path, firefighter_start, fire_goal)
            continuous_path = generate_continuous_path(sparse_path, grid)
            if continuous_path:
                clean_path = self.remove_consecutive_duplicates(continuous_path)
                # print(clean_path)
                self.firefighter.path = clean_path
            end_time = time.time()
            prm_times.append(end_time - start_time)
        if self.firefighter.path is not None:
            if len(self.firefighter.path) <= 1:
                self.firefighter.ticks_spot += 1
                if self.firefighter.ticks_spot > 20:
                    self.grid_map[self.firefighter.next_target[0], self.firefighter.next_target[1]] = EXTINGUISHED
                    pos = self.firefighter.next_target
                    if pos in self.fire_timers:
                        del self.fire_timers[pos]

                    self.firefighter.path = None
                    self.firefighter.ticks_spot = 0
        burn_duration = 485
        for pos, ignite_tick in list(self.fire_timers.items()):
            if self.tick_count - ignite_tick >= burn_duration:
                self.grid_map[(pos)] = BURNED
                del self.fire_timers[pos]
                r, c = pos
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4-connected neighbors
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < self.grid_map.shape[0] and 0 <= nc < self.grid_map.shape[1]):
                        if self.grid_map[nr, nc] != BURNED and (nr, nc) not in self.fire_timers:
                            self.grid_map[nr, nc] = FIRE
                            self.fire_timers[(nr, nc)] = self.tick_count
    def remove_consecutive_duplicates(self, path):
        if not path:
            return []
        cleaned = [path[0]]
        for point in path[1:]:
            if point != cleaned[-1]:
                cleaned.append(point)
        return cleaned
    def count_score(self):
        grid = np.array(self.grid_map)  

        wombus_points = np.where((grid == BURNED) | (grid == FIRE))
        firefighter_points = np.where(grid == EXTINGUISHED)

        wombus_score = len(wombus_points[0])  
        firefighter_score = len(firefighter_points[0])

        print(f"Wombus burned {wombus_score} pieces of forest")
        print(f"The firefighters put out {firefighter_score} of Wombus's fires")
        return wombus_score, firefighter_score
    def run(self):
        self.delay = 1
        self.world_setup()
        self.renderer.start_game(self.grid_map)
        loop_num = 0
        # path, nodes, graph_edges = prm_planner(self.grid_map, self.start, self.goal, num_samples=100, connection_radius=15)
        self.delay = 1
        while self.running:  ##infinite loop while running
            self.tick_count += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.path_characters()
            # print(self.wombus.path)
            self.move_characters()

            self.renderer.update_screen(self.status, self.grid_map, self.characters, self.goal, prm_data=(None))
            if self.tick_count % 1000 == 0:
                print(self.tick_count)
            if self.tick_count >= 8000: #3600 seconds worth of ticks
                self.running = False
            # pygame.time.wait(self.delay) 
            # self.clock.tick(1000)  
            pygame.display.flip()
          
        plot_planner_times(prm_times, astar_times)
        pygame.quit()
        wombus_score, firefighter_score = self.count_score()
        return wombus_score, firefighter_score
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
import matplotlib.pyplot as plt

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
    firefighter_scores = []
    wombus_scores = []
    # args.tick_speed = 1/
    for i in range(num_simualtions):
        pygame.init
        graph_generator = grid.generate_graph(args.x_size, args.y_size, args.coverage, args.square_size)
        renderer_engine = renderer()
        game = game_run(graph_generator, renderer_engine, args.tick_speed, args.num_enemies, False)
        wombus_score, firefighter_score = game.run()
        wombus_scores.append(wombus_score)
        firefighter_scores.append(firefighter_score)
        if firefighter_score > wombus_score:
            print("Firefighter Victory")
            num_wins+= 1
        else:
            print("Wombus Won")
            num_losses +=1

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
