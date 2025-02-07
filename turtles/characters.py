import search_algorithms
import numpy as np
import random
debug = False
@staticmethod
def debug_print(reason, printey):
    if debug:
        print(f"{reason}:\n {printey}")
class character:
    def __init__(self, start_pos):
        self.start_pos = start_pos
        # self.map_world = map_world
        self.position = start_pos
        
        self.path = None
    def valid_position(self, new_pos, grid_world):
        rows, cols = grid_world.shape
        return 0 <= new_pos[0] < rows and 0 <= new_pos[1] < cols
    def move_character(self, new_pos, grid_world, character_value):
        if not self.valid_position(new_pos, grid_world):
            print("Invalid Move Position! Exiting Game.")
            return grid_world
        else:
            grid_world[self.position[0], self.position[1]] = 0  # Clear previous position
            self.position = new_pos
            grid_world[self.position[0], self.position[1]] = character_value  # Place character
            return grid_world

    def path_finding(self):
         raise NotImplementedError("Subclasses must implement path_finding()")



class hero(character):
    def __init__(self, start_pos):
        self.color = (0, 255, 0)
        super().__init__(start_pos)

    def path_finding(self, position, goal, grid_world):
        self.path = search_algorithms.a_star_search(position, goal, grid_world)

class enemy(character):
    
    def __init__(self, start_pos):
        self.boom_positions = [1, 3]
        self.status = 'alive'
        self.color = (255, random.randrange(0, 50), random.randrange(0,25))
        super().__init__(start_pos)

    def move_character(self, new_pos, grid_world, character_value):
        if not self.valid_position(new_pos, grid_world):
            print("Invalid Move Position! Exiting Game.")
            return grid_world, 'alive'
        
        if grid_world[new_pos] in self.boom_positions:
            print("The enemy got destroyed!") 
            grid_world[self.position[0], self.position[1]] = 1  # Convert old position into obstacle
            return grid_world, 'destroyed'
            
        grid_world[self.position[0], self.position[1]] = 0  # Clear old position
        self.position = new_pos
        grid_world[self.position[0], self.position[1]] = character_value  # Move enemy
        return grid_world, 'alive'
    def path_finding(self,pose, grid_world, hero_position):
        ##remove all obstacles from the world and only leave the location of the hero

        enemy_grid_world = np.zeros(grid_world.shape, dtype=int)

        enemy_grid_world[hero_position] = 2
        self.path = search_algorithms.a_star_search(pose, hero_position, enemy_grid_world)
        

    










#     class character:
#     def __init__(self, start_pos, map_world, goal_pos,debug):
#         self.start_pos = start_pos
#         self.map_world = map_world
#         self.position = start_pos
#         self.goal = goal_pos
#         self.path = []
#         self.debug = debug
#     def move_character(self, new_pos, grid_world):
#         if new_pos[0] >= len(self.map_world) or new_pos[1] >= len(self.map_world[0]):
#             print("Invalid Move Position Exiting Game!")
#             return False
#         else:
#             self.position = new_pos
#             new_world_grid = grid_world
#             new_world_grid[new_pos[0], new_pos[1]] = 2
#             return new_world_grid
#     def path_finding(self):
#         pass



# class hero(character):
#     def __init__(self, start_pos, map_world, goal_pos, debug):
#         super().__init__(start_pos, map_world, goal_pos, debug)

#     def path_finding(self, map_world):
#         maps_rows = len(self.map_world)
#         map_cols = len(self.map_world[0]) 
#         self.path = search_algorithms.a_star_search(self.start_pos, self.goal, maps_rows, map_cols, self.map_world, self.debug)
#         print("path", self.path)

# class enemy(character):
#     def __init__(self, start_pos, map_world, goal_pos, debug):
#         super().__init__(start_pos, map_world, goal_pos, debug)
#     def path_finding(self):
        
#         return super().path_finding()