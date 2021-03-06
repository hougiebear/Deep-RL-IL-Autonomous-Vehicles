import gym
import highway_env
import numpy as np
import argparse
from stable_baselines3 import A2C
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.results_plotter import load_results, ts2xy
import matplotlib.pyplot as plt
from stable_baselines3.common import results_plotter
from stable_baselines3.common.env_util import make_vec_env


 
    
params = {
    "environment": "parking-v0",
    "model_name": "A2C",
    "train_steps": 500000,
    "learning_rate": 0.01875150062,
    "n_steps": 64,
    "gamma": 0.98,
    "gae_lambda": 0.95,
    "ent_coef": 5.25E-05,
    "vf_coef": 0.8241157845,
    "max_grad_norm":  0.6,
    "rms_prop_eps":  1e-5,
    "use_rms_prop": False,
    "use_sde": False,
    "sde_sample_freq": -1,
    "normalize_advantage":  True,
    "create_eval_env": False,
    "policy": "MlpPolicy"

}

env = make_vec_env(params.get("environment"), n_envs=4)


log_dir = '../../../logs/' + params.get("model_name")
exp_name = params.get("model_name") + "_train_" + params.get("environment")


def train(params):

    model = A2C(params.get("policy"), env,
                verbose=1,
                tensorboard_log=log_dir,
                learning_rate=params.get("learning_rate"),
                n_steps=params.get("n_steps"),
                gamma= params.get("gamma"),
                gae_lambda=params.get("gae_lambda"),
                ent_coef=params.get("ent_coef"),
                vf_coef=params.get("vf_coef"),
                max_grad_norm=params.get("max_grad_norm"),
                rms_prop_eps=params.get("rms_prop_eps"),
                use_rms_prop=params.get("use_rms_prop"),
                use_sde=params.get("use_sde"),
                sde_sample_freq=params.get("sde_sample_freq"),
                normalize_advantage=params.get("normalize_advantage"),
                policy_kwargs=dict(net_arch=[64, 64]))

    # Train for 1e5 steps
    model.learn(total_timesteps=params.get("train_steps"))
    # Save the trained agent
    model.save(exp_name)

def evaluate(params):

    # Load saved model
    model = A2C.load(exp_name, env=env)
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
