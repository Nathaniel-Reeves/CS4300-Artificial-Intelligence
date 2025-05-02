#!/usr/bin/env python3

import gymnasium as gym
from pettingzoo.classic import connect_four_v3
import argparse
import logging
import sys
import time

def create_environment(render_mode, seed=None):
    env = connect_four_v3.env(render_mode=render_mode)
    if seed:
        env.reset(seed)
    return env

def destroy_environment(env):
    env.close()
    return

def run_one_episode(env, agent0, agent1):
    agents = { 'player_0': agent0, 'player_1': agent1 }
    times = { 'player_0': 0.0, 'player_1': 0.0 }
    env.reset()
    agent0.reset()
    agent1.reset()
    
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        if termination or truncation:
            action = None
            break
        
        t1 = time.time()
        action = agents[agent].agent_function(observation, agent)
        t2 = time.time()
        times[agent] += t2 - t1
        
        env.step(action)
    
    winner = None
    if len(env.rewards.keys()) == 2:
        for a in env.rewards:
            if env.rewards[a] == 1:
                winner = a
                break
    
    # for agent in times:
    #   print(f"Agent {agent} took {times[agent]:8.5f} seconds.")
    
    return winner

def run_many_episodes(env, episode_count, agent0, agent1):
    winners = {}
    for i in range(episode_count):
        winner = run_one_episode(env, agent0, agent1)
        if winner not in winners:
            winners[winner] = 0
        winners[winner] += 1
    destroy_environment(env)
    return winners

def parse_args(argv):
    parser = argparse.ArgumentParser(prog=argv[0], description='Connect Four Runner')
    parser.add_argument(
        "--episode-count",
        "-c",
        type=int,
        help="number of episodes to run",
        default=1
    )
    parser.add_argument(
        '--seed',
        type=str,
        default=None,
        nargs='?',
        help='seed for the environmen\'s PRNG'
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
        "--render-mode",
        "-r",
        choices=["human", "none"],
        type=str,
        default='human',
    )
    parser.add_argument(
        "--agent0",
        "-a",
        type=str,
        help="agent function: random, predictable, unpredictable, human",
        choices=["random", "predictable", "unpredictable", "human"],
        default="random"
    )
    parser.add_argument(
        "--agent1",
        "-A",
        type=str,
        help="agent function: random, predictable, unpredictable, human",
        choices=["random", "predictable", "unpredictable", "human"],
        default="random"
    )

    my_args = parser.parse_args(argv[1:])
    if my_args.logging_level == "warn":
        my_args.logging_level = logging.WARN
    elif my_args.logging_level == "info":
        my_args.logging_level = logging.INFO
    elif my_args.logging_level == "debug":
        my_args.logging_level = logging.DEBUG
        
    return my_args

from agent_random import AgentRandom
from agent_predictable import AgentPredictable
from agent_unpredictable import AgentUnpredictable
from agent_human import AgentHuman

def select_agent(agent_name):
    if agent_name == "random":
        agent_function = AgentRandom()
    elif agent_name == "predictable":
        agent_function = AgentPredictable()
    elif agent_name == "unpredictable":
        agent_function = AgentUnpredictable()
    elif agent_name == "human":
        agent_function = AgentHuman()
    else:
        raise ValueError(f"Unknown agent: {agent_name}")
    return agent_function

def main(argv):
    my_args = parse_args(argv)
    logging.basicConfig(level=my_args.logging_level)
    
    env = create_environment(my_args.render_mode, my_args.seed)
    agent0 = select_agent(my_args.agent0)
    agent1 = select_agent(my_args.agent1)
    winners = run_many_episodes(env, my_args.episode_count, agent0, agent1)
    winners['player_0'] = winners.get('player_0', 0)
    winners['player_1'] = winners.get('player_1', 0)
    print(f"Winners: A0:{winners['player_0']} A1:{winners['player_1']}")
    return

if __name__ == "__main__":
    main(sys.argv)