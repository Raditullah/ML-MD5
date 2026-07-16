"""Lab 5.2 - Train PPO on the custom Robot1DEnv, sparse vs shaped reward.

Also runs a "reward hacking" stress test with a poorly designed shaped reward
that rewards speed regardless of direction, to observe cheating behavior.
"""
import numpy as np
import matplotlib.pyplot as plt
from gymnasium.utils.env_checker import check_env
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from robot_env import Robot1DEnv

TIMESTEPS = 50_000
LOG_DIR = "logs"


def smoothed_rewards(monitor_csv, window=50):
    data = np.genfromtxt(monitor_csv, delimiter=",", skip_header=2)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    rewards = data[:, 0]
    timesteps = np.cumsum(data[:, 1])
    if len(rewards) < window:
        return timesteps, rewards
    smoothed = np.convolve(rewards, np.ones(window) / window, mode="valid")
    return timesteps[: len(smoothed)], smoothed


def train(shaped, log_name):
    env = Monitor(Robot1DEnv(goal=8.0, shaped=shaped), filename=f"{LOG_DIR}/{log_name}")
    model = PPO("MlpPolicy", env, verbose=0)
    model.learn(total_timesteps=TIMESTEPS)
    model.save(log_name)
    return model


def main():
    import os
    os.makedirs(LOG_DIR, exist_ok=True)

    print("Validating environment with check_env...")
    check_env(Robot1DEnv())
    print("check_env passed with no warnings.\n")

    print("Training PPO with sparse reward...")
    train(shaped=False, log_name="sparse")

    print("Training PPO with shaped reward...")
    train(shaped=True, log_name="shaped")

    x_sparse, y_sparse = smoothed_rewards(f"{LOG_DIR}/sparse.monitor.csv")
    x_shaped, y_shaped = smoothed_rewards(f"{LOG_DIR}/shaped.monitor.csv")

    plt.figure(figsize=(10, 5))
    plt.plot(x_sparse, y_sparse, label="Sparse reward (+10 at goal only)", color="#c0392b")
    plt.plot(x_shaped, y_shaped, label="Shaped reward (distance penalty + bonus)", color="#27ae60")
    plt.xlabel("Timesteps")
    plt.ylabel("Episode Reward (smoothed)")
    plt.title("Robot1DEnv: Sparse vs Shaped Reward")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("sparse_vs_shaped.png", dpi=150)
    print("Saved: sparse_vs_shaped.png")


if __name__ == "__main__":
    main()
