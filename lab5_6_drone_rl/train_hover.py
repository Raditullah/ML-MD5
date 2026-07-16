import os
import time
import argparse
import gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold

# Import simulator drone
from gym_pybullet_drones.envs.single_agent_rl.HoverAviary import HoverAviary
from gym_pybullet_drones.utils.Logger import Logger
from gym_pybullet_drones.utils.utils import sync

DEFAULT_GUI = True
DEFAULT_RECORD_VIDEO = False
DEFAULT_OUTPUT_FOLDER = 'results'
DEFAULT_COLAB = False

def run(gui=DEFAULT_GUI, record_video=DEFAULT_RECORD_VIDEO, output_folder=DEFAULT_OUTPUT_FOLDER, colab=DEFAULT_COLAB):
    # Membuat folder output jika belum ada
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 1. Inisialisasi Environment untuk Training
    # macOS M3 kadang bermasalah dengan GUI PyBullet saat training paralel, 
    # oleh karena itu GUI dinonaktifkan (False) khusus saat proses training agar super cepat.
    train_env = make_vec_env(HoverAviary,
                             env_kwargs=dict(gui=False, record=record_video),
                             n_envs=1,
                             seed=0
                             )

    # 2. Setup Model PPO (Proximal Policy Optimization)
    # Menyesuaikan dengan model zip yang kamu miliki 'pybullet_hover_ppo.zip'
    model_path = os.path.join(output_folder, "pybullet_hover_ppo.zip")
    
    if os.path.exists(model_path):
        print(f"[*] Menemukan model pre-trained di {model_path}. Melanjutkan training...")
        model = PPO.load(model_path, env=train_env)
    else:
        print("[*] Membuat model PPO baru...")
        model = PPO('MlpPolicy',
                    train_env,
                    tensorboard_log=os.path.join(output_folder, "tb_logs"),
                    verbose=1)

    # 3. Proses Training (Silakan sesuaikan total_timesteps dengan kebutuhan tugas lab-mu)
    print("[*] Memulai proses training drone...")
    model.learn(total_timesteps=10000) # Bisa kamu naikkan misal ke 50000 atau 100000
    
    # Menyimpan hasil training
    model.save(model_path)
    print(f"[+] Model berhasil disimpan di {model_path}")

    # 4. Evaluasi Hasil Training (Menampilkan GUI Drone Terbang Hover)
    print("[*] Memulai evaluasi hasil training dengan GUI...")
    eval_env = HoverAviary(gui=gui, record=record_video)
    obs = eval_env.reset()
    start_time = time.time()
    
    for i in range(1000): # Jalankan simulasi visual selama 1000 step
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, info = eval_env.step(action)
        eval_env.render()
        if gui:
            sync(i, start_time, eval_env.TIMESTEP)
        if done:
            obs = eval_env.reset()
            
    eval_env.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hover RL training using PPO')
    parser.add_argument('--gui', default=DEFAULT_GUI, type=bool, help='Tampilkan GUI PyBullet (default: True)')
    parser.add_argument('--output_folder', default=DEFAULT_OUTPUT_FOLDER, type=str, help='Folder output hasil (default: results)')
    args = parser.parse_args()
    
    run(gui=args.gui, output_folder=args.output_folder)