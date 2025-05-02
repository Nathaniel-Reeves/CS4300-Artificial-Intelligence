#!/usr/bin/env python3

import gymnasium as gym
import argparse
import logging
import sys
import random
import time

from cliff_walking_model import CliffWalkingModel

def create_environment(max_episode_steps, render_mode):
    env = gym.make('CliffWalking-v0', render_mode=render_mode)
    if max_episode_steps:
        env = gym.wrappers.TimeLimit(env, max_episode_steps=max_episode_steps)
    return env

def destroy_environment(env):
    env.close()
    return

def run_one_episode(env, policy):
    observation, info = env.reset()
    terminated = False
    truncated = False
    total_reward = 0
    while not (terminated or truncated):
        action = policy.get_action(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
    return total_reward

def parse_args(argv):
    parser = argparse.ArgumentParser(prog=argv[0], description='Run Cliff Walker')
    parser.add_argument(
        '--neighbor-mode',
        '-n',
        type=str,
        default='all-rows',
        choices=['all-rows', 'next-row'],
        nargs='?',
        help='All Rows or Next Row'
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
        "--max-episode-steps",
        "-s",
        type=int,
        help="maximum number of episode steps (defaults to environment default)",
        default=40
    )
    parser.add_argument(
        "--restarts",
        "-r",
        type=int,
        default=1
    )
    parser.add_argument(
        "--render-mode",
        "-rm",
        type=str,
        help="display style (render mode): human, none",
        choices=("human", "none"),
        default="none",
    )

    my_args = parser.parse_args(argv[1:])
    if my_args.logging_level == "warn":
        my_args.logging_level = logging.WARN
    elif my_args.logging_level == "info":
        my_args.logging_level = logging.INFO
    elif my_args.logging_level == "debug":
        my_args.logging_level = logging.DEBUG
        
    return my_args

def set_neighbor_mode(my_args, model):
    if my_args.neighbor_mode == "all-rows":
        model.set_neighbors_all_rows()
    elif my_args.neighbor_mode == 'next-row':
        model.set_neighbors_next_row()
    return model

def HillClimbing(p0, model):
    """
    Find policy with largest obtainable utility function value.
    
    sudo code from curtis
    """
    
    current_policy = p0
    best_utility = float('inf')
    best_neighbour = None
    neighbors = model.NEIGHBORS(current_policy)
    while best_utility > 305:
        found_better_neighbour = False
        for neighbour in neighbors:
            utility = model.UTILITY(neighbour)
            if utility < best_utility:
                logging.info(f'New Best Utility: {utility}')
                best_utility = utility
                best_neighbour = neighbour
                neighbors = model.NEIGHBORS(best_neighbour)
                found_better_neighbour = True
        if not found_better_neighbour:
            logging.info('No Better Neighbour Found, Choosing Random Neighbour')
            return HillClimbing(model.RANDOM_POLICY(), model)
    
    return best_neighbour

def hillclimb(my_args):
    env = create_environment(my_args.max_episode_steps, my_args.render_mode)
    model = CliffWalkingModel(env)
    model = set_neighbor_mode(my_args, model)
    start = time.time()
    good_policy = HillClimbing(model.RANDOM_POLICY(), model)
    end = time.time()
    logging.info(f'Time: {end - start}')
    print(f'Solution: {good_policy}')
    print(f'Utility: {model.UTILITY(good_policy)}')
    destroy_environment(env)
    return good_policy

def policy_search():
    env = create_environment(40, 'none')
    model = CliffWalkingModel(env)
    model.set_neighbors_all_rows()
    start = time.time()
    good_policy = HillClimbing(model.RANDOM_POLICY(), model)
    end = time.time()
    logging.info(f'Time: {end - start}')
    if end - start > 120:
        logging.warning(f'Time Limit Exceeded: {end-start} > 120s')
    logging.info(f'Solution: {good_policy}')
    logging.info(f'Utility: {model.UTILITY(good_policy)}')
    destroy_environment(env)
    return good_policy.get_policy()

def main(argv):
    my_args = parse_args(argv)
    logging.basicConfig(level=my_args.logging_level)
    
    # Find the best policy
    logging.info('Starting Hill Climb...')
    good_policy = hillclimb(my_args)
    logging.info('Hill Climb Complete')
    
    # Run environment with best policy
    logging.info('Running Environment...')
    env = create_environment(my_args.max_episode_steps, 'human')
    total_reward = run_one_episode(env, good_policy)
    logging.info(f'Total Reward: {total_reward}')
    destroy_environment(env)
    logging.info('Environment Complete')
    return

if __name__ == "__main__":
    main(sys.argv)
