"""Lab 5.1 - Classic Control with Stable-Baselines3.

Trains DQN and PPO on CartPole-v1, compares learning curves, evaluates,
and runs a gamma ablation (0.9 vs 0.99).
"""
import time

import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy

TIMESTEPS = 50_000
LOG_DIR = "logs"


def make_env(log_name):
    env = gym.make("CartPole-v1")
    return Monitor(env, filename=f"{LOG_DIR}/{log_name}")


def train_and_time(algo_cls, algo_name, **kwargs):
    env = make_env(algo_name)
    model = algo_cls("MlpPolicy", env, verbose=0, **kwargs)
    start = time.time()
    model.learn(total_timesteps=TIMESTEPS)
    elapsed = time.time() - start
    model.save(f"{algo_name}_cartpole")
    print(f"{algo_name}: trained {TIMESTEPS} steps in {elapsed:.1f}s")
    return model, elapsed


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


def evaluate(model, n_episodes=10):
    env = gym.make("CartPole-v1")
    mean_r, std_r = evaluate_policy(model, env, n_eval_episodes=n_episodes)
    env.close()
    return mean_r, std_r


def main():
    import os
    os.makedirs(LOG_DIR, exist_ok=True)

    dqn_model, dqn_time = train_and_time(DQN, "dqn")
    ppo_model, ppo_time = train_and_time(PPO, "ppo")

    # Plot DQN vs PPO learning curves
    dqn_x, dqn_y = smoothed_rewards(f"{LOG_DIR}/dqn.monitor.csv")
    ppo_x, ppo_y = smoothed_rewards(f"{LOG_DIR}/ppo.monitor.csv")

    plt.figure(figsize=(10, 5))
    plt.plot(dqn_x, dqn_y, label="DQN", color="#e67e22")
    plt.plot(ppo_x, ppo_y, label="PPO", color="#003366")
    plt.xlabel("Timesteps")
    plt.ylabel("Episode Reward (smoothed, window=50)")
    plt.title("DQN vs PPO on CartPole-v1")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("dqn_vs_ppo.png", dpi=150)
    print("Saved: dqn_vs_ppo.png")

    # Evaluation table
    dqn_mean, dqn_std = evaluate(dqn_model)
    ppo_mean, ppo_std = evaluate(ppo_model)
    print("\n=== Evaluation (10 episodes) ===")
    print(f"DQN: {dqn_mean:.1f} +/- {dqn_std:.1f}")
    print(f"PPO: {ppo_mean:.1f} +/- {ppo_std:.1f}")

    # Gamma ablation on PPO
    print("\n=== Gamma ablation (PPO) ===")
    env_low = make_env("ppo_gamma09")
    model_low = PPO("MlpPolicy", env_low, gamma=0.9, verbose=0)
    model_low.learn(total_timesteps=TIMESTEPS)

    env_high = make_env("ppo_gamma099")
    model_high = PPO("MlpPolicy", env_high, gamma=0.99, verbose=0)
    model_high.learn(total_timesteps=TIMESTEPS)

    x_low, y_low = smoothed_rewards(f"{LOG_DIR}/ppo_gamma09.monitor.csv")
    x_high, y_high = smoothed_rewards(f"{LOG_DIR}/ppo_gamma099.monitor.csv")

    plt.figure(figsize=(10, 5))
    plt.plot(x_low, y_low, label="gamma=0.9 (short-sighted)", color="#c0392b")
    plt.plot(x_high, y_high, label="gamma=0.99 (far-sighted)", color="#27ae60")
    plt.xlabel("Timesteps")
    plt.ylabel("Episode Reward (smoothed)")
    plt.title("PPO Gamma Ablation on CartPole-v1")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("gamma_ablation.png", dpi=150)
    print("Saved: gamma_ablation.png")


if __name__ == "__main__":
    main()
