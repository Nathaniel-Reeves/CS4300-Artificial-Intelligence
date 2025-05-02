#!/usr/bin/env python3

import taxi_model as taxi
import logging

# MAKE CLASS Node
# MAKE CLASS Frontier

class Agent1:

    def __init__(self):
        """required, with no arguments to initialize correctly"""
        self.model = taxi.TaxiDrivingModel()
        self.max_depth = 10
        self.pickup_actions = []
        self.dropoff_actions = []
        return

    def reset(self):
        """required"""
        self.model.reset()
        self.max_depth = 10
        self.pickup_actions = []
        self.dropoff_actions = []
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
        return goal_found, action_sequence

    def ids(self, s0):
        logging.info("IDS: s0: ", s0)
        # NODE: (state, parent_node, action, depth)
        parent_node =  (s0, None, None, 0)
        
        goal_found = False
        action_sequence = []
        current_level = 0
        max_level = 1

        while not goal_found and max_level <= self.max_depth:
            goal_found, action_sequence = self.idsr(current_level, max_level, parent_node, goal_found, action_sequence)
            max_level += 1

        logging.info("Action sequence: {}".format(action_sequence))
        logging.info("IDS: actions: ", action_sequence)
        return action_sequence
    
    def bfs(self, s0):
        logging.info("DFS: s0: ", s0)
        goal_node = None
        # NODE: (state, parent_node, action, depth)
        frontier = [ (s0, None, None, 0) ]
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
        logging.info("Action sequence: {}".format(action_sequence))
        logging.info("DFS: actions: ", action_sequence)
        return action_sequence

    def agent_function(self, state):
        """required"""
        max_depth = self.max_depth
        taxi_row, taxi_col, passenger_location, destination = self.model.decode_state(state)
        
        # Pickup Passenger
        if taxi.ACTION_PICKUP in self.model.ACTIONS(state):
            logging.info("Pickup Passenger")
            return taxi.ACTION_PICKUP
        
        # Drop off Passenger
        if taxi.ACTION_DROPOFF in self.model.ACTIONS(state):
            logging.info("Drop off Passenger")
            return taxi.ACTION_DROPOFF
        
        # Go to Passenger
        if passenger_location != taxi.L_TAXI:
            # Calculate Pickup
            if len(self.pickup_actions) == 0:
                logging.info("Calculating Pickup")
                self.pickup_actions = self.ids(state)
            if len(self.pickup_actions) == 0:
                logging.warn("IDS Search failed.")
                raise Exception("IDS Search failed.")
            else:
                logging.info("Pickup actions: {}".format(self.pickup_actions))
            
            # Execute Pickup
            action = self.pickup_actions.pop()
        
        # Go to Destination
        if passenger_location == taxi.L_TAXI:
            # Calculate Drop Off
            if len(self.dropoff_actions) == 0:
                logging.info("Calculating Dropoff")
                self.dropoff_actions = self.ids(state)
            if len(self.dropoff_actions) == 0:
                logging.warn("IDS Search failed.")
                raise Exception("IDS Search failed.")
            else:
                logging.info("Dropoff actions: {}".format(self.dropoff_actions))
            
            # Execute Drop Off
            if len(self.dropoff_actions) == 0:
                logging.warn("Dropoff actions are empty.")
                raise Exception("Dropoff actions are empty.")
            action = self.dropoff_actions.pop()
        
        if action is None:
            logging.warn("state: {}".format(state))
            raise Exception("Oof!")
        return action
    