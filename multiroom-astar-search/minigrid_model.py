#!/usr/bin/env python3
from __future__ import annotations
import logging

import numpy as np

TILE_PIXELS = 32

# Map of color names to RGB values
COLORS = {
    "red": np.array([255, 0, 0]),
    "green": np.array([0, 255, 0]),
    "blue": np.array([0, 0, 255]),
    "purple": np.array([112, 39, 195]),
    "yellow": np.array([255, 255, 0]),
    "grey": np.array([100, 100, 100]),
}

COLOR_NAMES = sorted(list(COLORS.keys()))

# Used to map colors to integers
COLOR_TO_IDX = {"red": 0, "green": 1, "blue": 2, "purple": 3, "yellow": 4, "grey": 5}

IDX_TO_COLOR = dict(zip(COLOR_TO_IDX.values(), COLOR_TO_IDX.keys()))

# Map of object type to integers
OBJECT_TO_IDX = {
    "unseen": 0,
    "empty": 1,
    "wall": 2,
    "floor": 3,
    "door": 4,
    "key": 5,
    "ball": 6,
    "box": 7,
    "goal": 8,
    "lava": 9,
    "agent": 10,
}

IDX_TO_OBJECT = dict(zip(OBJECT_TO_IDX.values(), OBJECT_TO_IDX.keys()))

# Map of state names to integers
STATE_TO_IDX = {
    "open": 0,
    "closed": 1,
    "locked": 2,
}

# Map of agent direction indices to vectors
DIR_TO_VEC = [
    # Pointing right (positive X)
    np.array((1, 0)),
    # Down (positive Y)
    np.array((0, 1)),
    # Pointing left (negative X)
    np.array((-1, 0)),
    # Up (negative Y)
    np.array((0, -1)),
]

# Actions
ACTION_TURN_LEFT = 0
ACTION_TURN_RIGHT = 1
ACTION_MOVE_FORWARD = 2
ACTION_PICKUP = 3
ACTION_DROP = 4
ACTION_TOGGLE = 5
ACTION_UNUSED = 6
ALL_ACTIONS = [ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_MOVE_FORWARD, ACTION_TOGGLE]

DIRECTION_RIGHT = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_UP = 3

DOOR_OPEN = 0
DOOR_CLOSED = 1
DOOR_LOCKED = 2

def wait(dev_mode=0):
    if dev_mode:
        print()
        input("Press Enter to continue...")
        print()
        print()
    return

# python3 main.py -r human -l debug -a agent1 --seed 12
# https://docs.google.com/spreadsheets/d/1SjMxN9OjDxRFuUhfRXom1nzZcl2X5QQdos89GhO-TeA/edit?gid=0#gid=0

class MiniGridModel:

    def __init__(self, decoded_state):
        self.agent_x = decoded_state["agent_x"]
        self.agent_y = decoded_state["agent_y"]
        self.agent_direction = decoded_state["agent_direction"]
        self.goal_x = decoded_state["goal_x"]
        self.goal_y = decoded_state["goal_y"]
        self.doors = decoded_state["doors"]
        self.walls = decoded_state["walls"]
        self.cal_facing_cords(self.agent_x, self.agent_y, self.agent_direction)
    
    def reset(self):
        self.agent_x = None
        self.agent_y = None
        self.facing_x = None
        self.facing_y = None
        self.goal_x = None
        self.goal_y = None
        self.doors = []
    
    def update_state(self, decoded_state):
        self.agent_x = decoded_state["agent_x"]
        self.agent_y = decoded_state["agent_y"]
        self.agent_direction = decoded_state["agent_direction"]
        self.goal_x = decoded_state["goal_x"]
        self.goal_y = decoded_state["goal_y"]
        self.doors = decoded_state["doors"]
        self.walls = decoded_state["walls"]
        self.cal_facing_cords(self.agent_x, self.agent_y, self.agent_direction)

    def cal_facing_cords(self, x, y, direction):
        if direction == DIRECTION_RIGHT:
            self.facing_x = x + 1
            self.facing_y = y
        elif direction == DIRECTION_DOWN:
            self.facing_x = x
            self.facing_y = y + 1
        elif direction == DIRECTION_LEFT:
            self.facing_x = x - 1
            self.facing_y = y
        elif direction == DIRECTION_UP:
            self.facing_x = x
            self.facing_y = y - 1
        else:
            raise ValueError(f"Invalid Direction: {direction}")

    def ACTIONS(self, state):
        logging.debug("------ CALLING ACTIONS ------")
        self.update_state(state)
        
        actions = [ACTION_TURN_LEFT, ACTION_TURN_RIGHT]
        
        self.cal_facing_cords(self.agent_x, self.agent_y, self.agent_direction)
        
        key = f"{self.facing_x},{self.facing_y}"
        
        door_locations = self.doors.keys()
        if key in door_locations:
            if self.doors[key] == DOOR_OPEN:
                actions.append(ACTION_MOVE_FORWARD)
            elif self.doors[key] == DOOR_CLOSED:
                actions.append(ACTION_TOGGLE)
            else:
                logging.warning("Invalid Door State")
        
        elif key not in self.walls:
            actions.append(ACTION_MOVE_FORWARD)
        
        logging.debug(f"Legal Actions: {[self.action_to_string(action) for action in actions]}")
        logging.debug("-----------------------------\n")
        wait()
        return actions

    def GOAL_TEST(self, state):
        logging.debug("------ CALLING GOAL TEST ------")
        logging.debug(f"Goal At: x:{self.goal_x}, y:{self.goal_y}")
        self.update_state(state)
        
        flag = False
        
        all_doors_open = True
        for key in self.doors:
            if self.doors[key] == DOOR_CLOSED:
                all_doors_open = False
                break
        
        if self.agent_x == self.goal_x and self.agent_y == self.goal_y and all_doors_open:
            flag = True
        
        key = f"{self.facing_x},{self.facing_y}"
        
        if key in self.doors:
            if self.doors[key] == DOOR_CLOSED:
                flag = True

        logging.debug(f"Goal Found Status: {flag}")
        logging.debug("-----------------------------\n")
        wait()
        return flag
    
    def action_to_string(self, action):
        if action == ACTION_TURN_LEFT:
            return 'Turn Left'
        if action == ACTION_TURN_RIGHT:
            return 'Turn Right'
        if action == ACTION_MOVE_FORWARD:
            return 'Move Forward'
        if action == ACTION_TOGGLE:
            return 'Toggle'
        raise ValueError(f"Invalid Action: {action}")

    def RESULT(self, state, action):
        logging.debug("------ CALLING RESULT ------")
        self.update_state(state)

        a = self.action_to_string(action)
        logging.debug(f"Taking Action: {a}")
        
        new_state = state.copy()
        
        if action == ACTION_TURN_LEFT:
            new_state['agent_direction'] = (self.agent_direction - 1) % 4
        
        elif action == ACTION_TURN_RIGHT:
            new_state['agent_direction'] = (self.agent_direction + 1) % 4
        
        elif action == ACTION_MOVE_FORWARD:
            self.cal_facing_cords(self.agent_x, self.agent_y, self.agent_direction)
            key = f"{self.facing_x},{self.facing_y}"
            
            if not key in self.walls:
                new_state['agent_x'] = self.facing_x
                new_state['agent_y'] = self.facing_y
            else:
                logging.warning("Tried to move into a wall")
        
        elif action == ACTION_TOGGLE:
            key = f"{self.facing_x},{self.facing_y}"
            if key in self.doors:
                if self.doors[key] == DOOR_OPEN:
                    new_state['doors'][key] = DOOR_CLOSED
                elif self.doors[key] == DOOR_CLOSED:
                    new_state['doors'][key] = DOOR_OPEN
                else:
                    logging.warning("Invalid Door State")
            else:
                logging.warning("Door Not Found")
        
        logging.debug("\n")
        logging.debug(f"New State after: {a}")
        
        logging.debug("-----------------------------\n")
        wait()
        return new_state
    
    def STEP_COST(self, state, action, next_state):
        logging.debug("------ CALLING STEP COST ------")
        self.update_state(state)
        
        move_cost = 1
        
        logging.debug("-----------------------------\n")
        wait()
        return move_cost
    
    def HEURISTIC(self, state):
        logging.debug("------ CALLING HERISTIC ------")
        self.update_state(state)
        
        # distance formula between agent facing and goal SCORE: .45 - .63
        d = abs(self.agent_x - self.goal_x) + abs(self.agent_y - self.goal_y)
        
        # # find nearest closed door SCORE: .20 - .45
        # all_doors_open = True
        # min_door_distance = 100000
        # for key in self.doors:
        #     if self.doors[key] == DOOR_CLOSED:
        #         all_doors_open = False
        #         x, y = key.split(',')
        #         door_distance = abs(self.agent_x - int(x)) + abs(self.agent_y - int(y))
        #         if door_distance < min_door_distance:
        #             min_door_distance = door_distance
        
        # # set heuristic to nearest closed door if it is closer than the goal
        # if min_door_distance < d and not all_doors_open:
        #     d = min_door_distance
        
        # Cumilitive Heuristic SCORE .70 - .72
        temp_doors = self.doors.copy()
        total_d = 0
        
        # find nearest closed door
        while temp_doors:
            d, key = self.find_nearest_door(temp_doors)
            temp_doors.pop(key)
            x, y = key.split(',')
            
            # Ignore open doors
            if self.doors[key] == DOOR_OPEN:
                continue
            
            total_d += d
            
            # if last door, add distance to goal
            if not temp_doors:
                total_d += abs(self.goal_x - int(x)) + abs(self.goal_y - int(y))
        
        d = total_d
        
        # floor distance and return
        logging.debug(f"heuristic: {d}")
        
        logging.debug("-----------------------------\n")
        wait()
        return d

    def find_nearest_door(self, doors):
        min_door_distance = 100000
        for key in doors:
            x, y = key.split(',')
            door_distance = abs(self.agent_x - int(x)) + abs(self.agent_y - int(y))
            if door_distance < min_door_distance:
                min_door_distance = door_distance
                return min_door_distance, key