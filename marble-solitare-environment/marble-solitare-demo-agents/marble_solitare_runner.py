#!/usr/bin/env python3

import gymnasium as gym
import argparse
import marble_solitare
import logging
import sys
import time
import multiprocessing as mp
import numpy as np
import pandas as pd

def create_environment(render_mode, seed, max_episode_steps, board_type, theme):
    env = gym.make('marble_solitare/MarbleSolitare-v0', render_mode=render_mode, type=board_type, max_episode_steps=max_episode_steps, theme=theme)
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
        'marbles_left': 0,
        'success': False
    }
    
    while not (terminated or truncated):
        action = agent.agent_function(observation)
        if action is None:
            break
        observation, reward, terminated, truncated, info = env.step(action)
        if wait > 0:
            time.sleep(wait)
        elif wait < 0:
            input("Press Enter to continue...")
        # print('Terminated:', terminated)
        # print('Truncated:', truncated)
    
    result['reward'] = reward
    result['num_moves'] = observation['moves_made']
    result['marbles_left'] = observation['marbles_left']
    result['success'] = observation['marbles_left'] == 1
    
    return result

def run_many_episodes_with_multiprocessing(env, episode_count, agent, wait):
    reward_sum = 0
    num_moves_sum = 0
    marbles_left_sum = 0
    success_count = 0
    pool = mp.Pool(mp.cpu_count())
    results = []
    
    for i in range(episode_count):
        results.append(pool.apply_async(run_one_episode, args=(env, agent, wait)))
    
    for result in results:
        result_data = result.get()
        reward_sum += result_data['reward']
        num_moves_sum += result_data['num_moves']
        marbles_left_sum += result_data['marbles_left']
        if result_data['success']:
            success_count += 1
    
    destroy_environment(env)
    ave_reward = reward_sum / episode_count
    ave_num_moves = num_moves_sum / episode_count
    ave_marbles_left = marbles_left_sum / episode_count
    success_rate = success_count / episode_count
    
    ave_result = {
        'reward': ave_reward,
        'num_moves': ave_num_moves,
        'marbles_left': ave_marbles_left,
        'success_rate': success_rate
    }
    
    return ave_result

def run_many_episodes(env, episode_count, agent, wait):
    reward_sum = 0
    num_moves_sum = 0
    marbles_left_sum = 0
    success_count = 0
    
    for i in range(episode_count):
        result = run_one_episode(env, agent, wait)
        reward_sum += result['reward']
        num_moves_sum += result['num_moves']
        marbles_left_sum += result['marbles_left']
        if result['success']:
            success_count += 1
    
    destroy_environment(env)
    ave_reward = reward_sum / episode_count
    ave_num_moves = num_moves_sum / episode_count
    ave_marbles_left = marbles_left_sum / episode_count
    success_rate = success_count / episode_count
    
    ave_result = {
        'reward': ave_reward,
        'num_moves': ave_num_moves,
        'marbles_left': ave_marbles_left,
        'success_rate': success_rate
    }
    
    return ave_result

def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog='Marble Solitaire Runner', 
        description='Run the Marble Solitaire Environment with an agent.',
        epilog='Created by: Nathaniel Reeves in February of 2026 as a side project.'
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
        default=100
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
        help="display style (render mode): terminal, none",
        choices=("terminal", "none"),
        default="terminal",
    )
    parser.add_argument(
        "--agent",
        "-a",
        type=str,
        help="agent function: human, bfs, dfs",
        choices=(
            "human",
            "bfs",
            "dfs"
        ),
        default="human",
    )
    parser.add_argument(
        "--board-type",
        "-bt",
        type=str,
        help="board type: english, european, european_corner, or european_french",
        choices=('english', 'european', 'european_corner', 'european_french'),
        default='european_french',
    )
    parser.add_argument(
        "--wait",
        "-w",
        type=int,
        help="wait time in ms between steps",
        default=0
    )
    parser.add_argument(
        "--visualize",
        "-v",
        action="store_true",
        help="visualization mode for DFS: search until Enter pressed, then replay best solution with delays",
        default=False
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
    
    # board_type is already a string, no conversion needed
    
    my_args.wait = my_args.wait / 1000
    
    return my_args

from human_agent import HumanAgent
from bfs_agent import BFSAgent
from dfs_agent import DFSAgent

def select_agent(agent_name, visualize=False):
    if agent_name == "human":
        agent_function = HumanAgent()
    elif agent_name == "bfs":
        agent_function = BFSAgent()
    elif agent_name == "dfs":
        agent_function = DFSAgent(visualize=visualize)
    else:
        raise Exception(f"unknown agent name: {agent_name}")
    return agent_function

def run_n_games(agent_name, board_type, games):
    print(f'Running Agent:{agent_name} on {board_type} board')
    start = time.time()
    env = create_environment(None, 0, 100, board_type, None)
    agent = select_agent(agent_name)
    result = run_many_episodes_with_multiprocessing(env, games, agent, 0)
    result['agent'] = agent_name
    result['games'] = games
    result['board_type'] = board_type
    end = time.time()
    result['duration'] = end - start
    return result

def run_agent(agent_name, games, results):
    result = run_n_games(agent_name, 'english', games)
    results.append(result)
    result = run_n_games(agent_name, 'european', games)
    results.append(result)
    return results

def run_all_agents(games):
    # Run All Agents, with all board types
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

# python3 marble_solitare_runner.py -bt english -c 1 -a a3 -l info --seed 180
# Seed settings doesn't work unless you provide a logging level and wait time.

def main(argv):
    my_args = parse_args(argv)
    logging.basicConfig(level=my_args.logging_level)
    
    all_agents = False
    if all_agents:
        num_games = 1000
        run_all_agents(num_games)
        return

    env = create_environment(my_args.render_mode, my_args.seed, my_args.max_episode_steps, my_args.board_type, my_args.theme)
    agent = select_agent(my_args.agent, visualize=my_args.visualize)
    
    # For human agent, bfs, or dfs agent, use interactive mode (wait for Enter between moves)
    # unless in visualize mode, which has its own timing
    if my_args.agent in ['human', 'bfs', 'dfs']:
        if my_args.visualize and my_args.agent == 'dfs':
            my_args.wait = 2.0  # 2 second delay between moves in visualization mode
        else:
            my_args.wait = -1
    
    if my_args.wait == 0:
        result = run_many_episodes_with_multiprocessing(env, my_args.episode_count, agent, my_args.wait)
    else:
        result = run_many_episodes(env, my_args.episode_count, agent, my_args.wait)
    
    print(f"Average results: {result['reward']}")
    return

if __name__ == "__main__":
    main(sys.argv)
    

