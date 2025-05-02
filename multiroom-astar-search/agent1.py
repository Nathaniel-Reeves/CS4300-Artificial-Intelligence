# !/usr/bin/env python3

import minigrid_model as mgrid
import logging
from queue import PriorityQueue

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

class Node:
    def __init__(self):
        self.parent_node = None
        
        self.action = None
        self.state = None
        
        self.cost_and_heuristic = float('inf')
        self.total_cost = float('inf')
        self.heuristic = 0
    
    def __lt__(self, other):
        return self.cost_and_heuristic < other.cost_and_heuristic
    
    def calc_c_and_h(self):
        self.cost_and_heuristic = self.total_cost + self.heuristic

class Agent1:

    def __init__(self):
        """required, with no arguments to initialize correctly"""
        self.model = None
        self.max_depth = 100
        self.actions = []
        self.pq = PriorityQueue()
        self.stuck = False
        return

    def reset(self):
        """required"""
        self.model = None
        self.max_depth = 100
        self.actions = []
        self.pq = PriorityQueue()
        self.stuck = False
        return
    
    def idsr(self, current_level, max_level, node, goal_found, action_sequence):
        state, parent, action, depth = node
        
        if goal_found:
            action_sequence.append(action)
            return goal_found, action_sequence
        
        if current_level >= max_level:
            return goal_found, action_sequence

        for action in self.model.ACTIONS(state):
            new_state = self.model.RESULT(state, action)
            if self.model.GOAL_TEST(new_state):
                goal_found = True
                action_sequence.append(action)
                return goal_found, action_sequence
            else:
                node1 = (new_state, node, action, depth+1)
                goal_found, action_sequence = self.idsr(current_level+1, max_level, node1, goal_found, action_sequence)
                if goal_found:
                    action_sequence.append(action)
                    
        return goal_found, action_sequence

    def ids(self, s0):
        # NODE: (state, parent_node, action, depth)
        parent_node =  (s0, None, None, 0)
        
        goal_found = False
        action_sequence = []
        current_level = 0
        max_level = 1

        while not goal_found and max_level <= self.max_depth:
            logging.info(f"Calculating to Level: {max_level}")
            goal_found, action_sequence = self.idsr(current_level, max_level, parent_node, goal_found, action_sequence)
            logging.info(f"Goal Found: {goal_found}")
            if goal_found:
                logging.info(f"Actions: {action_sequence}")
            max_level += 1
            logging.info(f"\n")
            mgrid.wait()
        return action_sequence
    
    def bfs(self, s0):
        goal_node = None
        # NODE: (state, parent_node, action, depth)
        frontier = [ (s0, None, 0, 0) ]
        while len(frontier) > 0:
            node = frontier.pop()
            state, parent, action, depth = node
            if self.model.GOAL_TEST(state):
                goal_node = node
                break
            elif depth >= self.max_depth:
                # do not generate children
                continue
            for action in self.model.ACTIONS(state):
                state1 = self.model.RESULT(state, action)
                node1 = (state1, node, action, depth+1)
                frontier.append(node1)
        action_sequence = []
        if goal_node:
            node = goal_node
            while node[1] is not None and node[1][1] is not None:
                node = node[1]
                action_sequence.append(node[2])
            if node[1][1] is None:
                action_sequence.append(node[2])
        return action_sequence
    
    def a_star(self, s0):
        
        # Build Model
        model = mgrid.MiniGridModel(s0)
        
        # Initialize Agent Cell
        first_node = Node()
        
        first_node.action = None
        first_node.state = s0
        
        first_node.total_cost = 0
        first_node.heuristic = model.HEURISTIC(s0)
        first_node.calc_c_and_h()
        
        self.pq.put((first_node.cost_and_heuristic, first_node))
        
        goal_found = False
        
        while not goal_found:
            id, node = self.pq.get()
            
            if model.GOAL_TEST(node.state):
                goal_found = True
                break
            else:
                actions = model.ACTIONS(node.state)
                for action in actions:
                    new_node = Node()
                    new_node.state = model.RESULT(node.state, action)
                    new_node.parent_node = node
                    new_node.action = action
                    new_node.total_cost = node.total_cost + model.STEP_COST(node.state, action, new_node.state)
                    new_node.heuristic = model.HEURISTIC(new_node.state)
                    new_node.calc_c_and_h()
                    
                    self.pq.put((new_node.cost_and_heuristic, new_node))
                    
            mgrid.wait()
        
        if goal_found:
            action_sequence = []
            while node.parent_node is not None:
                if node.action is not None:
                     action_sequence.append(node.action)
                node = node.parent_node
            return action_sequence
        else:
            return [2]
    
    def decode_observation(self, observation):
        agent_direction = observation["direction"]
        agent_x = None
        agent_y = None
        
        goal_x = None
        goal_y = None
        
        doors = {}
        walls = []
        
        grid_width = observation["image"].shape[0]
        grid_height = observation["image"].shape[1]
        
        for x in range(grid_width):
            for y in range(grid_height):
                if IDX_TO_OBJECT[observation["image"][x][y][0]] == 'agent':
                    agent_x = x
                    agent_y = y

                if IDX_TO_OBJECT[observation["image"][x][y][0]] == 'goal':
                    goal_x = x
                    goal_y = y
                
                if IDX_TO_OBJECT[observation["image"][x][y][0]] == 'door':
                    doors[f'{x},{y}'] = observation["image"][x][y][2]
                
                if IDX_TO_OBJECT[observation["image"][x][y][0]] == 'wall':
                    walls.append(f'{x},{y}')
        return {
            "agent_x": agent_x,
            "agent_y": agent_y,
            "agent_direction": agent_direction,
            "goal_x": goal_x,
            "goal_y": goal_y,
            "doors": doors,
            "walls": walls
        }

    def agent_function(self, state):
        """required"""
        
        if self.stuck:
            self.actions = [2, 2]
            logging.info(f"Stuck: {self.actions}")
            mgrid.wait()
            self.stuck = False
        
        elif len(self.actions) == 0:
            logging.info("--------------------------------     Calculating Search...  ---------------------------------")
            decoded_state = self.decode_observation(state)
            self.actions = self.a_star(decoded_state)
            logging.info(f"Actions: {self.actions}")
            
            if len(self.actions) != 0:
                logging.info("--------------------------------     Search Calculated  ---------------------------------")
                self.actions = [2, 5, *self.actions]
                logging.info(f"Actions: {self.actions}")
                mgrid.wait()
            else:
                logging.info("No Actions Found")
                logging.info("--------------------------------    Search Failed  ---------------------------------")
                self.stuck = True
                return 5

        return self.actions.pop()
    