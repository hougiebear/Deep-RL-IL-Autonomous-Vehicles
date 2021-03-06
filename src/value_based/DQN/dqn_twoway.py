import gym
import highway_env
import numpy as np
import argparse
from stable_baselines3 import DQN
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.results_plotter import load_results, ts2xy
import matplotlib.pyplot as plt
from stable_baselines3.common import results_plotter

params = {
    "environment": "two-way-v0",
    "model_name": "DQN",
    "train_steps": 500000,
    "buffer_size": 100000,
    "batch_size": 32,
    "gamma": 0.995,
    "target_update_interval": 4,
    "train_freq": 256,
    "exploration_fraction": 0.334260855238745,
    "exploration_final_eps": 0.19775644605798,
    "learning_rate": 9.47951656573785E-05,
    "learning_starts": 0,
    "policy": "MlpPolicy",
    "gradient_steps": 1,
    "test_episodes": 10000
}

policy_kwargs = dict(net_arch=[256, 256])

env = gym.make(params.get("environment"))

exp_name = params.get("model_name") + "_train_" + params.get("environment")
log_dir = '../../../logs/' + exp_name


def train(params):

    model = DQN(params.get("policy"), env,
                verbose=1,
                buffer_size=params.get("buffer_size"),
                learning_rate=params.get("learning_rate"),
                tensorboard_log=log_dir,
                gamma=params.get("gamma"),
                target_update_interval=params.get("target_update_interval"),
                train_freq=params.get("train_freq"),
                gradient_steps=params.get("gradient_steps"),
                exploration_fraction=params.get("exploration_fraction"),
                exploration_final_eps=params.get("exploration_final_eps"),
                learning_starts=params.get("learning_starts"),
                batch_size=params.get("batch_size"),
                policy_kwargs=policy_kwargs
                )
    # Train for 1e5 steps
    model.learn(total_timesteps=params.get("train_steps"))
    # Save the trained agent
    model.save(exp_name)

def evaluate(params):

    # Load saved model
    model = DQN.load(exp_name, env=env)
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