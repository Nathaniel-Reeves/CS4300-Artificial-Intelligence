import gymnasium as gym
import random
import math

ACTION_PUSH_LEFT = 0
ACTION_NOOP = 1
ACTION_PUSH_RIGHT = 2
ACTIONS_ALL = [ACTION_PUSH_LEFT, ACTION_NOOP, ACTION_PUSH_RIGHT]

def unpack_observation(observation):
    position, velocity = observation
    return position, velocity

def random_agent(observation):
    action = random.choice(ACTIONS_ALL)
    return action

def left_agent(observation):
    return ACTION_PUSH_LEFT

def right_agent(observation):
    return ACTION_PUSH_RIGHT

def smart_agent(observation):
    position, velocity = unpack_observation(observation)
    center_x = -math.pi/6.0
    if position > center_x:
        return ACTION_PUSH_RIGHT
    elif position < center_x:
        return ACTION_PUSH_LEFT
    else:
        return ACTION_NOOP

def nothing_agent(observation):
    position, velocity = unpack_observation(observation)
    center_x = -math.pi/6.0
    if position < center_x and velocity < 0:
        return ACTION_PUSH_RIGHT
    elif position > center_x and velocity > 0:
        return ACTION_PUSH_LEFT
    else:
        return ACTION_NOOP

def smarter_agent(observation):
    position, velocity = unpack_observation(observation)
    center_x = -math.pi/6.0
    if position < center_x and velocity > 0:
        return ACTION_PUSH_RIGHT
    elif position > center_x and velocity < 0:
        return ACTION_PUSH_LEFT
    else:
        return ACTION_NOOP

def create_environment():
    env = gym.make('MountainCar-v0', render_mode='human')
    return env

def run_one_episode(env, agent_function):
    observation, info = env.reset()
    terminated = False
    truncated = False
    total_reward = 0
    while not (terminated or truncated):
        action = agent_function(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
    return total_reward

def destroy_environment(env):
    env.close()
    return

def main():
    agent_function = smart_agent
    agent_function = smarter_agent
    
    env = create_environment()
    episode_count = 1
    reward_sum = 0
    for i in range(episode_count):
        reward_sum += run_one_episode(env, agent_function)
    destroy_environment(env)
    reward = reward_sum / episode_count
    print('Average reward:', reward)
    return

if __name__ == '__main__':
    main()