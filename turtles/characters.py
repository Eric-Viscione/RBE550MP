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
    def move_character(self, new_pos, grid_world, character):
        if new_pos is not None:
            if new_pos[0] >= len(grid_world) or new_pos[1] >= len(grid_world[0]):
                print("Invalid Move Position Exiting Game!")
                return grid_world
            else:
                new_world_grid = np.copy(grid_world)
                new_world_grid[self.position[0], self.position[1]] = 0
                self.position = new_pos
                debug_print("Move to position", self.position)
                debug_print("Character value is ", character)
                new_world_grid[self.position[0], self.position[1]] = character
                debug_print("Heros movement updated in grid", new_world_grid)
                return new_world_grid
    def path_finding(self):
        pass



class hero(character):
    def __init__(self, start_pos):
        self.color = (0, 255, 0)
        super().__init__(start_pos)

    def path_finding(self, position, goal, grid_world):
       
        self.path = search_algorithms.a_star_search(position, goal, grid_world)
        debug_print("Hero Path found", self.path)

class enemy(character):
    
    def __init__(self, start_pos):
        self.boom_positions = [1, 3]
        self.status = 'alive'
        self.color = (255, random.randrange(0, 50), random.randrange(0,25))
        super().__init__(start_pos)
    def move_character(self, new_pos, grid_world, character):
        if new_pos is not None:
            if new_pos[0] >= len(grid_world) or new_pos[1] >= len(grid_world[0]):
                print("Invalid Move Position Exiting Game!")
                return grid_world
            else:
                new_world_grid = np.copy(grid_world)
                
                if grid_world[new_pos] in self.boom_positions: #if the enemy is going to hit an destroyer thing like an obstacle or another enemy create a new obstacle at the current position of the enemy
                    print("The enemy got destroyed!") 
                    new_world_grid[self.position[0], self.position[1]] = 1
                    return new_world_grid, 'destroyed'
                else:
                    new_world_grid[self.position[0], self.position[1]] = 0
                    self.position = new_pos
                    debug_print("Move Enemy to position", self.position)
                    debug_print("Enemy value is ", character)
                    new_world_grid[self.position[0], self.position[1]] = character
                    debug_print("Enemy movement updated in grid", new_world_grid)
                    return new_world_grid, 'alive'
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