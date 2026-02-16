#!/usr/bin/env python3
import random
import gymnasium as gym
import argparse
import logging
import sys
import os
import json

from cliff_policy_agent import PolicyAgent
import policy_search

def create_environment(render_mode, seed, max_episode_steps):
    env = gym.make('CliffWalking-v0g', render_mode=render_mode)
    if seed:
        env.reset(seed=seed)
    if max_episode_steps:
        env = gym.wrappers.TimeLimit(env, max_episode_steps=max_episode_steps)

    return env

def destroy_environment(env):
    env.close()
    return

def run_one_episode(env, agent):
    observation, info = env.reset()
    agent.reset()
    terminated = False
    truncated = False
    total_reward = 0
    while not (terminated or truncated):
        action = agent.agent_function(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
    return total_reward

def run_many_episodes(env, episode_count, agent):
    reward_sum = 0
    for i in range(episode_count):
        reward_sum += run_one_episode(env, agent)
    destroy_environment(env)
    reward = reward_sum / episode_count
    return reward

def parse_args(argv):
    parser = argparse.ArgumentParser(prog=argv[0], description='Policy Search and Execution for Cliff Walker')
    parser.add_argument('action', default='policy-search',
                        choices=[ 'policy-search', 'policy-measure' ],
                        nargs='?', help="desired action")
    parser.add_argument(
        "--episode-count",
        "-c",
        type=int, 
        help="number of episodes to run when measuring",
        default=1
    )
    parser.add_argument(
        "--max-episode-steps",
        "-s",
        type=int, 
        help="maximum number of episode steps (defaults to environment default)",
        default=50
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
        help="display style (render mode): human, none",
        choices=("human", "none"),
        default="human",
    )
    parser.add_argument(
        "--policy-file",
        "-p",
        type=str,
        help="file to store/load policy",
        default="",
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

    if my_args.action in ("policy-search", "policy-measure"):
        if my_args.policy_file == "":
            raise Exception("Must specify a policy file name.")

    return my_args

def load_policy(my_args):
    if os.path.exists(my_args.policy_file):
        with open(my_args.policy_file, "r") as read_file:
            policy = json.load(read_file)
    else:
        policy = [ random.choice([0,1,2,3]) for i in range(37) ]
    return policy

def save_policy(my_args, policy):
    with open(my_args.policy_file, "w") as write_file:
        json.dump(policy, write_file, indent=2)
    return

def select_agent(my_args):
    policy = load_policy(my_args)
    agent = PolicyAgent(policy)
    return agent

def do_policy_search(my_args):
    policy = policy_search.policy_search()
    save_policy(my_args, policy)
    print(policy)
    return

def do_policy_measure(my_args):
    env = create_environment(my_args.render_mode, my_args.seed, my_args.max_episode_steps)
    agent = select_agent(my_args)
    reward = run_many_episodes(env, my_args.episode_count, agent)
    print(f"Reward: {reward}")
    return

def main(argv):
    my_args = parse_args(argv)
    logging.basicConfig(level=my_args.logging_level)

    actions = {
        "policy-search": do_policy_search,
        "policy-measure": do_policy_measure,
    }
    if my_args.action in actions:
        actions[my_args.action](my_args)
    else:
        raise Exception("{} not in known actions.".format(my_args.action))

    return

if __name__ == "__main__":
    main(sys.argv)