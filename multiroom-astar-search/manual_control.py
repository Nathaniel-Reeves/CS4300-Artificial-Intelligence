#!/usr/bin/env python3

from __future__ import annotations

import gymnasium as gym
import pygame
from gymnasium import Env

from minigrid.core.actions import Actions
from minigrid.minigrid_env import MiniGridEnv
from minigrid.wrappers import ImgObsWrapper, RGBImgPartialObsWrapper
from minigrid.wrappers import FullyObsWrapper

import minigrid_model as mgrid

class ManualControl:
    def __init__(
        self,
        env: Env,
        seed=None,
    ) -> None:
        self.env = env
        self.seed = seed
        self.closed = False

    def start(self):
        """Start the window display with blocking event loop"""
        self.reset(self.seed)

        while not self.closed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.env.close()
                    break
                if event.type == pygame.KEYDOWN:
                    event.key = pygame.key.name(int(event.key))
                    self.key_handler(event)

    def step(self, action: Actions):
        state, reward, terminated, truncated, _ = self.env.step(action)
        print(f"step={self.env.step_count}, reward={reward:.2f}")

        # find agent
        for x in range(len(state['image'])):
            for y in range(len(state['image'][x])):
                if mgrid.IDX_TO_OBJECT[state['image'][x][y][0]] == 'agent':
                    print(f"agent cell: ", state['image'][x][y])
                    print("agent direction: ", state['direction'])
                    print(f"agent position: x:{x} y:{y}")
                    
                    fx = x
                    fy = y
                    if state['direction'] == mgrid.DIRECTION_RIGHT:
                        fx = x + 1
                    elif state['direction'] == mgrid.DIRECTION_DOWN:
                        fy = y + 1
                    elif state['direction'] == mgrid.DIRECTION_LEFT:
                        fx = x - 1
                    elif state['direction'] == mgrid.DIRECTION_UP:
                        fy = y - 1
                    else:
                        raise("Invalid direction")
                    
                    print(f"agent facing: x:{fx} y:{fy}")
                    print(f"facing: {mgrid.IDX_TO_OBJECT[state['image'][fx][fy][0]]}")
                    print(f"facing_cell: {state['image'][fx][fy]}")
                    break
                    
        mg = mgrid.MiniGridModel()
        actions = mg.ACTIONS(state)
        print_actions = []
        for action in actions:
            if action == 0:
                print_actions.append('Left')
            elif action == 1:
                print_actions.append('Right')
            elif action == 2:
                print_actions.append('Forward')
            elif action == 5:
                print_actions.append('Toggle')
            else:
                raise("Invalid action")
        print("avalible actions: ", print_actions) 
        
        print()
        goal = mg.GOAL_TEST(state)
        print("Goal Test:", goal)
        print()
        
        for action in actions:
            print("Action:", action)
            new_state = mg.RESULT(state, action)
            goal_state = mg.find_goal(new_state)
            print("Goal State:", goal_state)
            agent_state = mg.find_agent(new_state)
            print("Agent State:", agent_state)
            agent_direction = mg.get_agent_direction(new_state)
            print("Agent Direction:", agent_direction)
            agent_facing = mg.find_agent_facing(new_state)
            print("Agent Facing:", agent_facing)
            print()
            

        if terminated:
            print("terminated!")
            self.reset(self.seed)
        elif truncated:
            print("truncated!")
            self.reset(self.seed)
        else:
            self.env.render()
        
        print()
        print()

    def reset(self, seed=None):
        self.env.reset(seed=seed)
        self.env.render()

    def key_handler(self, event):
        key: str = event.key
        print("pressed", key)

        if key == "escape":
            self.env.close()
            return
        if key == "backspace":
            self.reset()
            return

        key_to_action = {
            "left": Actions.left,
            "right": Actions.right,
            "up": Actions.forward,
            "space": Actions.toggle,
            "pageup": Actions.pickup,
            "pagedown": Actions.drop,
            "tab": Actions.pickup,
            "left shift": Actions.drop,
            "enter": Actions.done,
        }
        if key in key_to_action.keys():
            action = key_to_action[key]
            self.step(action)
        else:
            print(key)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-id",
        type=str,
        help="gym environment to load",
        choices=gym.envs.registry.keys(),
        default="MiniGrid-MultiRoom-N6-v0",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="random seed to generate the environment with",
        default=None,
    )
    parser.add_argument(
        "--tile-size", type=int, help="size at which to render tiles", default=32
    )
    parser.add_argument(
        "--agent-view",
        action="store_true",
        help="draw the agent sees (partially observable view)",
    )
    parser.add_argument(
        "--agent-view-size",
        type=int,
        default=7,
        help="set the number of grid spaces visible in agent-view ",
    )
    parser.add_argument(
        "--screen-size",
        type=int,
        default="640",
        help="set the resolution for pygame rendering (width and height)",
    )

    args = parser.parse_args()

    env: MiniGridEnv = gym.make(
        args.env_id,
        tile_size=args.tile_size,
        render_mode="human",
        agent_pov=args.agent_view,
        agent_view_size=args.agent_view_size,
        screen_size=args.screen_size,
    )

    # TODO: check if this can be removed
    if args.agent_view:
        print("Using agent view")
        env = RGBImgPartialObsWrapper(env, args.tile_size)
        env = ImgObsWrapper(env)
    env = FullyObsWrapper(env)

    manual_control = ManualControl(env, seed=args.seed)
    manual_control.start()