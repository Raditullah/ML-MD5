"""Lab 5.1 - Exploration ablation: DQN with epsilon_end=0.01 vs 0.1.

Answers the module's Analysis Assignment Part A, point 5: does more
permanent exploration help or hurt final DQN performance on CartPole-v1?
"""
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import DQN
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy
import gymnasium as gym

TIMESTEPS = 50_000
LOG_DIR = "logs"


def make_env(log_name):
    env = gym.make("CartPole-v1")
    return Monitor(env, filename=f"{LOG_DIR}/{log_name}")


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


def train_and_eval(eps_end, log_name):
    env = make_env(log_name)
    model = DQN("MlpPolicy", env, exploration_final_eps=eps_end, verbose=0)
    model.learn(total_timesteps=TIMESTEPS)
    eval_env = gym.make("CartPole-v1")
    mean_r, std_r = evaluate_policy(model, eval_env, n_eval_episodes=10)
    eval_env.close()
    return mean_r, std_r


def main():
    import os
    os.makedirs(LOG_DIR, exist_ok=True)

    print("Training DQN with exploration_final_eps=0.01 ...")
    mean_low, std_low = train_and_eval(0.01, "dqn_eps001")

    print("Training DQN with exploration_final_eps=0.1 ...")
    mean_high, std_high = train_and_eval(0.1, "dqn_eps01")

    print("\n=== Evaluation (10 episodes) ===")
    print(f"eps_end=0.01: {mean_low:.1f} +/- {std_low:.1f}")
    print(f"eps_end=0.10: {mean_high:.1f} +/- {std_high:.1f}")

    x_low, y_low = smoothed_rewards(f"{LOG_DIR}/dqn_eps001.monitor.csv")
    x_high, y_high = smoothed_rewards(f"{LOG_DIR}/dqn_eps01.monitor.csv")

    plt.figure(figsize=(10, 5))
    plt.plot(x_low, y_low, label="eps_end=0.01 (mostly greedy)", color="#8e44ad")
    plt.plot(x_high, y_high, label="eps_end=0.10 (more exploration)", color="#16a085")
    plt.xlabel("Timesteps")
    plt.ylabel("Episode Reward (smoothed)")
    plt.title("DQN Exploration Ablation on CartPole-v1")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("epsilon_ablation.png", dpi=150)
    print("Saved: epsilon_ablation.png")


if __name__ == "__main__":
    main()
