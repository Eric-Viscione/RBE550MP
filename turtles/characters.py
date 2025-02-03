import search_algorithms


class character:
    def __init__(self, start_pos, map_world, goal_pos,debug):
        self.start_pos = start_pos
        self.map_world = map_world
        self.position = start_pos
        self.goal = goal_pos
        self.path = []
        self.debug = debug
    def move_character(self, new_pos):
        if new_pos[0] >= len(self.map_world) or new_pos[1] >= len(self.map_world[0]):
            print("Invalid Move Position Exiting Game!")
            return False
        else:
            self.position = new_pos
            return True
    def path_finding(self):
        pass



class hero(character):
    def __init__(self, start_pos, map_world, goal_pos, debug):
        super().__init__(start_pos, map_world, goal_pos, debug)

    def path_finding(self):
        maps_rows = len(self.map_world)
        map_cols = len(self.map_world[0]) 
        self.path = search_algorithms.a_star_search(self.start_pos, self.goal, maps_rows, map_cols, self.map_world, self.debug)
        print("path", self.path)

class enemy(character):
    def __init__(self, start_pos, map_world, goal_pos, debug):
        super().__init__(start_pos, map_world, goal_pos, debug)
    def path_finding(self):
        
        return super().path_finding()