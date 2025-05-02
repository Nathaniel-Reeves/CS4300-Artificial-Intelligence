import gymnasium as gym
import random

ACTION_NOOP = 0
ACTION_FIRE_LEFT = 1
ACTION_FIRE_MAIN = 2
ACTION_FIRE_RIGHT = 3
ACTIONS_ALL = [ACTION_NOOP, ACTION_FIRE_LEFT, ACTION_FIRE_MAIN, ACTION_FIRE_RIGHT]

WIDTH       = 1000  # 600
HEIGHT      = 1000  # 400 
WIN_SIZE    = (WIDTH, HEIGHT)

def unpack_observation(observation):
    x, y, delta_x, delta_y, angle, delta_angle, left_leg, right_leg = observation
    return x, y, delta_x, delta_y, angle, delta_angle, left_leg, right_leg 

def random_agent(observation):
    action = random.choice(ACTIONS_ALL)
    return action

def floating_agent(observation):
    x, y, delta_x, delta_y, angle, delta_angle, left_leg, right_leg = unpack_observation(observation)
    if delta_y < 0 and y < 1:
        return ACTION_FIRE_MAIN
    elif delta_angle < 0:
        return ACTION_FIRE_LEFT
    elif delta_angle > 0:
        return ACTION_FIRE_RIGHT
    elif delta_x < 0:
        return ACTION_FIRE_LEFT
    elif delta_x > 0:
        return ACTION_FIRE_RIGHT
    else:
        return ACTION_NOOP

def landing_agent(observation):
    x, y, delta_x, delta_y, angle, delta_angle, left_leg, right_leg = unpack_observation(observation)
    
    # obs = f'x:{x:7.3f}   y:{y:7.3f}   dx:{delta_x:7.3f}   dy:{delta_y:7.3f}   a:{angle:7.3f}   da:{delta_angle:7.3f}   l:{left_leg}   r:{right_leg}'
    # print(obs)

    if left_leg and right_leg:
        return ACTION_NOOP
    
    if delta_y < -0.15:
        return ACTION_FIRE_MAIN
    elif angle < 0.02 and x > 0.1 or angle < -0.05:
        return ACTION_FIRE_LEFT
    elif angle > -0.02 and x < -0.1 or angle > 0.05:
        return ACTION_FIRE_RIGHT
    else:
        return ACTION_NOOP

evil_turned_over = False
def missle_agent(observation):
    x, y, delta_x, delta_y, angle, delta_angle, left_leg, right_leg = unpack_observation(observation)
    
    # obs = f'x:{x:7.3f}   y:{y:7.3f}   dx:{delta_x:7.3f}   dy:{delta_y:7.3f}   a:{angle:7.3f}   da:{delta_angle:7.3f}   l:{left_leg}   r:{right_leg}'
    # print(obs)
    
    global evil_turned_over
    
    if delta_y < -0.15 and not evil_turned_over:
        evil_turned_over = True
        return ACTION_FIRE_MAIN
    
    if angle > -1.5:
        return ACTION_FIRE_RIGHT
    elif delta_angle < 0:
        return ACTION_FIRE_LEFT
    else:
        return ACTION_FIRE_MAIN

def create_environment():
    # env = gym.make('LunarLander-v2', render_mode='human')
    env = gym.make('LunarLander-v2')
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
    agent_function = missle_agent
    
    env = create_environment()
    episode_count = 50
    reward_sum = 0
    for i in range(episode_count):
        reward_sum += run_one_episode(env, agent_function)
    destroy_environment(env)
    reward = reward_sum / episode_count
    print('Average reward:', reward)
    return

if __name__ == '__main__':
    main()