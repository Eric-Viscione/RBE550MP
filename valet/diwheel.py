from grid import make_defined_grid
from ackerman_planner import visualize_path, diwheel_planner
for _ in range(5):
    start = (10,100,270)
    goal = (75,10,0)
    grid_size = (120,120)


    obstacles = [(90, 30, 120, 40), (60, 0, 80, 40), (5,50, 20, 68 ), (5,80, 20, 100 )]

    vehicle_size = (5.2,1.8)
    grid = make_defined_grid(grid_size,(start[0], start[1]), (goal[0], goal[1]),  vehicle_size,obstacles, rand_obstacles=True,rand_number=25, simple=False)

    # visualize_path(None, grid)
    diwheel_planner(start, goal, grid,vehicle_size)
# ackerman_planner(start, goal, grid, vehicle_size)
