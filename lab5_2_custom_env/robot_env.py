"""Lab 5.2 - Custom Gymnasium environment: 1D robot reaching a goal.

Option A from the module: a robot on a line must reach a goal position.
Includes both a sparse-reward and a shaped-reward variant to compare.
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np


class Robot1DEnv(gym.Env):
    """A 1D robot that must reach a goal position.

    Observation: [position, goal] (both in [-10, 10]).
    Action: 0 = move left, 1 = move right.
    Reward: sparse (+10 on arrival) or shaped (distance penalty + arrival bonus).
    """

    def __init__(self, goal=8.0, max_steps=100, shaped=False):
        super().__init__()
        self.goal = goal
        self.max_steps = max_steps
        self.shaped = shaped
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(
            low=np.array([-10, -10], dtype=np.float32),
            high=np.array([10, 10], dtype=np.float32),
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.position = 0.0
        self.steps = 0
        return self._get_obs(), {}

    def step(self, action):
        self.position += 1.0 if action == 1 else -1.0
        self.steps += 1
        distance = abs(self.position - self.goal)
        terminated = distance < 0.5
        truncated = self.steps >= self.max_steps

        if self.shaped:
            reward = -distance * 0.1
            if terminated:
                reward += 10.0
        else:
            reward = 10.0 if terminated else 0.0

        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        return np.array([self.position, self.goal], dtype=np.float32)
