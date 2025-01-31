from __future__ import annotations
from minigrid.core.constants import COLOR_NAMES
from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Door, Goal, Key, Wall
from minigrid.manual_control import ManualControl
from minigrid.minigrid_env import MiniGridEnv



class SimpleEnv(MiniGridEnv):
    def __init__(self,
                 size=8, 
                 agent_start_pos=(1, 1),
                 agent_start_dir=0,
                 max_steps: int | None = 256,
                 **kwargs):
        self.agent_start_pos = agent_start_pos
        self.agent_start_dir = agent_start_dir
        mission_space = MissionSpace(mission_func=self._gen_mission)
        self.valid_states = ['free', 'obstacle', 'junk', 'goal', 'hero', 'robot']
        self.state = 'free'  # Default initial state
        self.step_count = 0

        # Initialize the parent class
        super().__init__(
            mission_space=mission_space,
            grid_size=size,
            max_steps=max_steps,
            **kwargs
        )

    @staticmethod
    def _gen_mission():
        return "Complete the Grand Mission"

    def update_state(self, new_state):
        if new_state in self.valid_states:
            self.state = new_state
            return self.state
        else:
            raise ValueError(f"Invalid state: {new_state}. Valid states are {self.valid_states}.")

    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)
        self.agent_dir = self.agent_start_dir
        # Initialize the grid cells as 'free'
        for i in range(width):
            for j in range(height):
                self.grid.set(i, j, None)  # Set all cells initially to empty
        
        # Add a wall boundary
        self.grid.wall_rect(0, 0, width, height)
        
        # Place the agent
        if self.agent_start_pos is not None:
            self.agent_pos = self.agent_start_pos
            self.agent_dir = self.agent_start_dir
        else:
            self.place_agent()

        # Add a vertical wall in the middle of the grid
        for i in range(height):
            self.grid.set(5, i, Wall())


def main():
    env = SimpleEnv(render_mode="human")
    action = 2  # Move forward
    obs, reward, done, info = env.step(action)

    # Render the environment
    env.render()


if __name__ == "__main__":
    main()

