from grid import make_defined_grid
from ackerman_planner import trailer_planner, visualize_path




scale = 1
grid_size = (120,120)
start = (10,100,270)
goal = (75,10,0)
# obstacles = [(95,80,108,90), (90,107,110,120)] #y1, x1, y2, x2
# obstacles = [(25, 119, 35, 80)]
obstacles = [(90, 30, 120, 40), (60, 0, 80, 40), (5,50, 20, 65 ), (5,85, 20, 100 )]
# obstacles = []
vehicle_size = (5.4,2.0)
trailer_size = (4.5, 2.0)
grid = make_defined_grid(grid_size, start=(start[0], start[1]), end=(goal[0], goal[1]), 
                          vehicle_size=vehicle_size, obstacles=obstacles,
                            rand_obstacles=True,rand_number=25, simple=False)


# visualize_path(None, grid, start, goal, car_size=vehicle_size, trailer_size=trailer_size)


trailer_planner(start, goal, grid, vehicle_size, trailer_size)
