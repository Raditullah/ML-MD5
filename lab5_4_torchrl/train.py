"""Lab 5.4 - TorchRL Introduction (Optional).

Minimal PPO-style data collection pipeline on CartPole using TorchRL's
PyTorch-native primitives: GymEnv, SyncDataCollector, Actor.
Runs on CPU / Apple Silicon MPS -- no NVIDIA GPU required.
"""
import torch
import torch.nn as nn
from torchrl.envs import GymEnv
from torchrl.collectors import SyncDataCollector
from torchrl.modules import Actor

FRAMES_PER_BATCH = 200
TOTAL_FRAMES = 10_000


def main():
    env = GymEnv("CartPole-v1")

    actor_net = nn.Sequential(
        nn.Linear(4, 64), nn.Tanh(),
        nn.Linear(64, 2),
    )
    actor = Actor(actor_net, in_keys=["observation"])

    collector = SyncDataCollector(
        env, actor,
        frames_per_batch=FRAMES_PER_BATCH,
        total_frames=TOTAL_FRAMES,
    )

    print(f"Collecting {TOTAL_FRAMES} frames in batches of {FRAMES_PER_BATCH}...")
    batch_rewards = []
    for i, batch in enumerate(collector):
        mean_reward = batch["next", "reward"].mean().item()
        batch_rewards.append(mean_reward)
        print(f"Batch {i}: keys={list(batch.keys())} | mean_reward={mean_reward:.3f}")

    print("\nDone. TensorDict batch structure confirmed working on this machine.")
    print(f"Mean reward across all batches: {sum(batch_rewards)/len(batch_rewards):.3f}")
    collector.shutdown()


if __name__ == "__main__":
    main()
