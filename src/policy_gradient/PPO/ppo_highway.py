import gym
import highway_env
import numpy as np
import argparse
from stable_baselines3 import PPO
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.results_plotter import load_results, ts2xy
import matplotlib.pyplot as plt
from stable_baselines3.common import results_plotter
from stable_baselines3.common.env_util import make_vec_env


params = {
    "environment": "highway-v0",
    "model_name": "PPO",
    "train_steps": 200000,
    "batch_size": 32,
    "clip_range": 0.1,
    "ent_coef": 0.00007,
    "gae_lambda": 9,
    "gamma": 0.95,
    "learning_rate": 0.00087,
    "max_grad_norm": 0.9,
    "n_epochs": 20,
    "n_steps": 128,
    "sde_sample_freq": 64,
    "vf_coef": 0.557588101099478,
    "policy": "MlpPolicy"

}

policy_kwargs = dict(net_arch=[128, 128])

env = gym.make(params.get("environment"))
multi_env = make_vec_env(params.get("environment"), n_envs=4)

exp_name = params.get("model_name") + "_train_" + params.get("environment")
log_dir = '../../../logs/' + exp_name

def train(params):

    model = PPO(params.get("policy"), env,
                verbose=1,
                tensorboard_log=log_dir,
                batch_size=params.get("batch_size"),
                clip_range=params.get("clip_range"),
                ent_coef= params.get("ent_coef"),
                gae_lambda=params.get("gae_lambda"),
                gamma=params.get("gamma"),
                learning_rate=params.get("learning_rate"),
                max_grad_norm=params.get("max_grad_norm"),
                n_epochs=params.get("n_epochs"),
                n_steps=params.get("n_steps"),
                sde_sample_freq=params.get("sde_sample_freq"),
                vf_coef=params.get("vf_coef")
                ,policy_kwargs=dict(net_arch=[128, 128])
                )

    # Train for 1e5 steps
    model.learn(total_timesteps=params.get("train_steps"))
    # Save the trained agent
    model.save(exp_name)


def evaluate(params):

    # Load saved model
    model = PPO.load(exp_name, env=env)
    results = np.zeros(shape=(0,0))
    obs = env.reset()

    # Evaluate the agent
    episode_reward = 0
    for _ in range(params.get("test_episodes")):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        episode_reward += reward
        if done or info.get('is_success', False):
            episode_reward = 0.0
            obs = env.reset()

        result = ("Reward:", episode_reward, "Success?", info.get('is_success', True))
        results = np.append(results, result, axis=None)


def moving_average(values, window):
    """
    Smooth values by doing a moving average
    :param values: (numpy array)
    :param window: (int)
    :return: (numpy array)
    """
    weights = np.repeat(1.0, window) / window
    return np.convolve(values, weights, 'valid')


def plot_results(log_dir, title='Learning Curve'):
    """
    plot the results

    :param log_folder: (str) the save location of the results to plot
    :param title: (str) the title of the task to plot
    """
    x, y = ts2xy(load_results(log_dir), 'timesteps')
    y = moving_average(y, window=50)
    # Truncate x
    x = x[len(x) - len(y):]

    fig = plt.figure(title)
    plt.plot(x, y)
    plt.xlabel('Number of Timesteps')
    plt.ylabel('Rewards')
    plt.title(title + " Smoothed")
    plt.show()


def sb3_plot():
    results_plotter.plot_results([log_dir], 1e5, results_plotter.X_TIMESTEPS, exp_name)


train(params)
#evaluate(params)
