#!/usr/bin/env python3

import gymnasium as gym
import argparse
import spider_solitare
import logging
import sys
import time
import multiprocessing as mp
import numpy as np
import pandas as pd

def create_environment(render_mode, seed, max_episode_steps, num_suits, theme):
    env = gym.make('spider_solitare/SpiderSolitare-v0', render_mode=render_mode, num_suits=num_suits, max_episode_steps=max_episode_steps, theme=theme)
    if seed:
        env.reset(seed=seed)
    return env

def destroy_environment(env):
    env.close()
    return

def run_one_episode(env, agent, wait):
    observation, info = env.reset()
    agent.reset()
    terminated = False
    truncated = False
    
    result = {
        'reward': 0,
        'num_moves': 0,
        'num_completed_suits': 0
    }
    
    while not (terminated or truncated):
        action = agent.agent_function(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        if wait > 0:
            time.sleep(wait)
        elif wait < 0:
            input("Press Enter to continue...")
        # print('Terminated:', terminated)
        # print('Truncated:', truncated)
    
    result['reward'] = reward
    result['num_moves'] = observation['num_moves']
    completed_suits = observation['completed_suits']
    for suit in completed_suits.values():
        if len(suit) == 13:
            result['num_completed_suits'] += 1
    
    return result

def run_many_episodes_with_multiprocessing(env, episode_count, agent, wait):
    reward_sum = 0
    num_moves_sum = 0
    completed_suits_sum = 0
    pool = mp.Pool(mp.cpu_count())
    results = []
    
    for i in range(episode_count):
        results.append(pool.apply_async(run_one_episode, args=(env, agent, wait)))
    
    for result in results:
        reward_sum += result.get()['reward']
        num_moves_sum += result.get()['num_moves']
        completed_suits_sum += result.get()['num_completed_suits']
    
    destroy_environment(env)
    ave_reward = reward_sum / episode_count
    ave_num_moves = num_moves_sum / episode_count
    ave_completed_suits = completed_suits_sum / episode_count
    
    ave_result = {
        'reward': ave_reward,
        'num_moves': ave_num_moves,
        'num_completed_suits': ave_completed_suits
    }
    
    return ave_result

def run_many_episodes(env, episode_count, agent, wait):
    reward_sum = 0
    num_moves_sum = 0
    completed_suits_sum = 0
    
    for i in range(episode_count):
        result = run_one_episode(env, agent, wait)
        reward_sum += result['reward']
        num_moves_sum += result['num_moves']
        completed_suits_sum += result['num_completed_suits']
    
    destroy_environment(env)
    ave_reward = reward_sum / episode_count
    ave_num_moves = num_moves_sum / episode_count
    ave_completed_suits = completed_suits_sum / episode_count
    
    ave_result = {
        'reward': ave_reward,
        'num_moves': ave_num_moves,
        'num_completed_suits': ave_completed_suits
    }
    
    return ave_result

def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog='Spider Solitare Runner', 
        description='Run the Spider Solitare Environment with an agent.',
        epilog='Created by: Nathaniel Reeves in November of 2024 for a CS 4300\nArtificial Inteligence class project at Utah Tech University.'
    )
    parser.add_argument(
        "--episode-count",
        "-c",
        type=int, 
        help="number of episodes to run",
        default=1
    )
    parser.add_argument(
        "--max-episode-steps",
        "-s",
        type=int, 
        help="maximum number of episode steps (defaults to environment default)",
        default=700
    )
    parser.add_argument(
        "--logging-level",
        "-l",
        type=str,
        help="logging level: warn, info, debug",
        choices=("warn", "info", "debug"),
        default="warn",
    )
    parser.add_argument(
        "--seed",
        type=int, 
        help="seed for the environment's PRNG",
        default=0
    )
    parser.add_argument(
        "--render-mode",
        "-r",
        type=str,
        help="display style (render mode): ansi, none",
        choices=("ansi", "none"),
        default="ansi",
    )
    parser.add_argument(
        "--agent",
        "-a",
        type=str,
        help="agent function: random, ids",
        choices=(
            "random",
            "r",
            "human",
            "a0",
            "a1",
            "a2",
            "a3"
        ),
        default="random",
    )
    parser.add_argument(
        "--num-suits",
        "-ns",
        type=str,
        help="number of suits in the deck",
        choices=('1', '2', '4'),
        default='4',
    )
    parser.add_argument(
        "--wait",
        "-w",
        type=int,
        help="wait time in ms between steps",
        default=0
    )
    parser.add_argument(
        "--theme",
        "-t",
        type=str,
        help="color theme for the environment",
        choices=("light", "dark"),
        default="dark"
    )

    my_args = parser.parse_args(argv[1:])
    if my_args.logging_level == "warn":
        my_args.logging_level = logging.WARN
    elif my_args.logging_level == "info":
        my_args.logging_level = logging.INFO
    elif my_args.logging_level == "debug":
        my_args.logging_level = logging.DEBUG

    if my_args.render_mode == "none":
        my_args.render_mode = None
    
    if my_args.num_suits == '1':
        my_args.num_suits = 1
    elif my_args.num_suits == '2':
        my_args.num_suits = 2
    elif my_args.num_suits == '4':
        my_args.num_suits = 4
    
    my_args.wait = my_args.wait / 1000
    
    return my_args

from random_agent import RandomAgent
from human_agent import HumanAgent
from a0_custom_agent import ZeroCustomAgent
from a1_custom_agent import OneCustomAgent
from a2_custom_agent import TwoCustomAgent
from a3_custom_agent import ThreeCustomAgent

def select_agent(agent_name):
    if agent_name == "random" or agent_name == "r":
        agent_function = RandomAgent()
    elif agent_name == "human":
        agent_function = HumanAgent()
    elif agent_name == "a0":
        agent_function = ZeroCustomAgent()
    elif agent_name == "a1":
        agent_function = OneCustomAgent()
    elif agent_name == "a2":
        agent_function = TwoCustomAgent()
    elif agent_name == "a3":
        agent_function = ThreeCustomAgent()
    else:
        raise Exception(f"unknown agent name: {agent_name}")
    return agent_function

def run_n_games(agent_name, num_suits, games):
    print(f'Running Agent:{agent_name} on {num_suits} suit')
    start = time.time()
    env = create_environment(None, 0, 750, num_suits, None)
    agent = select_agent(agent_name)
    result = run_many_episodes_with_multiprocessing(env, games, agent, 0)
    result['agent'] = agent_name
    result['games'] = games
    result['suits'] = num_suits
    end = time.time()
    result['durration'] = end - start
    return result

def run_agent(agent_name, games, results):
    result = run_n_games(agent_name, 1, games)
    results.append(result)
    result = run_n_games(agent_name, 2, games)
    results.append(result)
    result = run_n_games(agent_name, 4, games)
    results.append(result)
    return results

def run_all_agents(games):
    # Run All Agents, with all suits
    results = []

    # Run Random Agent
    results = run_agent('r', games, results)
    
    # Run Custom Agent 0
    results = run_agent('a0', games, results)
    
    # Run Custom Agent 1
    results = run_agent('a1', games, results)
    
    # Run Custom Agent 2
    results = run_agent('a2', games, results)
    
    # Run Custom Agent 3
    results = run_agent('a3', games, results)
    
    print('Saving Data')
    
    # create a pandas dataframe
    df = pd.DataFrame(results)
    
    # save the dataframe to a csv file
    df.to_csv('final_results.csv')
    
    # save the dataframe to a pickle file
    df.to_pickle('final_results.pkl')
    
    print('Done')
    print(df)

# python3 spider_solitare_runner.py -ns 1 -c 1 -a a3 -l info --seed 180
# Seed settings doesn't work unless you provide a logging level and wait time.

def main(argv):
    my_args = parse_args(argv)
    logging.basicConfig(level=my_args.logging_level)
    
    all_agents = False
    if all_agents:
        num_games = 1000
        run_all_agents(num_games)
        return

    env = create_environment(my_args.render_mode, my_args.seed, my_args.max_episode_steps, my_args.num_suits, my_args.theme)
    agent = select_agent(my_args.agent)
    
    if my_args.wait == 0:
        result = run_many_episodes_with_multiprocessing(env, my_args.episode_count, agent, my_args.wait)
    else:
        result = run_many_episodes(env, my_args.episode_count, agent, my_args.wait)
    
    print(f"Average results: {result['reward']}")
    return

if __name__ == "__main__":
    main(sys.argv)
    

