#!/usr/bin/env python3

import spider_solitare
import logging
import random

class PickupNode:
    
    def __init__(self):
        self.parent_node = None
        self.action = None
        self.observation = None
        self.depth = 0

class PutdownNode:
    
    def __init__(self):
        self.parent_node = None
        self.action = None
        self.observation = None
        self.score = float('-inf')
        self.depth = 0
        self.goal = False
    
    def __lt__(self, other):
        return self.score < other.score
    
    def __eq__(self, other):
        return self.score == other.score
    
    def __gt__(self, other):
        return self.score > other.score
    
    def __le__(self, other):
        return self.score <= other.score
    
    def __ge__(self, other):
        return self.score >= other.score

class ZeroCustomAgent:
    
    def __init__(self):
        """required method"""
        self.model = spider_solitare.SpiderSolitareModel()
        self.max_depth = 14
        self.actions = []
        self.num_piles = 0
        self.putdown_nodes = []
        return
    
    def reset(self):
        """required method"""
        self.model = spider_solitare.SpiderSolitareModel()
        self.max_depth = 14
        self.actions = []
        self.num_piles = 0
        self.putdown_nodes = []
        return
    
    def HANDLE_PICKUP_NODE(self, node):
        # Unpack Node
        action = node.action
        observation = node.observation
        depth = node.depth
        
        if depth == self.max_depth:
            return
        
        actions = self.model.ACTIONS(observation)
        for action in actions:
            if action == 0:
                continue
            if action > 0 and action <= self.num_piles:
                new_node = PickupNode()
                new_node.action = action
                new_node.observation = self.model.RESULT(observation, action)
                new_node.depth = depth + 1
                new_node.parent_node = node
                self.HANDLE_PICKUP_NODE(new_node)
            if action > self.num_piles:
                new_node = PutdownNode()
                new_node.action = action
                new_node.observation = self.model.RESULT(observation, action)
                new_node.parent_node = node
                new_node.score = self.model.EVALUATE(new_node.observation)
                new_node.goal = self.model.GOAL_TEST(new_node.observation)
                new_node.depth = depth + 1
                self.putdown_nodes.append(new_node)

    def custom_search(self, observation):
        self.num_piles = self.model.NUM_PILES(observation)
        
        actions = self.model.ACTIONS(observation)
        self.max_score = self.model.EVALUATE(observation)
        
        # Generate Pickup Nodes
        process_nodes = []
        for action in actions:
            if action == 0:
                continue
            if action > 0 and action <= self.num_piles:
                pickup_node = PickupNode()
                pickup_node.action = action
                pickup_node.observation = self.model.RESULT(observation, action)
                pickup_node.depth = 1
                process_nodes.append(pickup_node)
            if action > self.num_piles:
                continue
        
        # Process Pickup Nodes
        for node in process_nodes:
            self.HANDLE_PICKUP_NODE(node)
        
        # Filter all putdown nodes that have a score less than the max score
        filtered_putdown_nodes = [node for node in self.putdown_nodes if node.score >= self.max_score]
        
        if len(filtered_putdown_nodes) == 0:
            self.actions = [0]
            return
        
        # Select the best putdown node and generate the action sequence
        selected_node = self.select_best_putdown_node(filtered_putdown_nodes)
        computed_actions = self.generate_action_sequence(selected_node)
        
        # Cycle through actions until a new valid sequence is found
        while True:
            filtered_putdown_nodes.remove(selected_node)
            if len(filtered_putdown_nodes) == 0:
                computed_actions = [0]
                break
            if self.validate_actions(observation, computed_actions):
                break
            selected_node = self.select_best_putdown_node(filtered_putdown_nodes)
            computed_actions = self.generate_action_sequence(selected_node)

        self.actions = computed_actions
    
    def select_best_putdown_node(self, nodes):
        max_node = max(nodes)
        
        r_node = random.choice(nodes)
        while r_node.score < max_node.score:
            r_node = random.choice(nodes)
        max_node = r_node
        
        return max_node

    def generate_action_sequence(self, max_node):
        computed_actions = []
        while max_node is not None:
            computed_actions.append(max_node.action)
            max_node = max_node.parent_node
        return computed_actions
    
    def validate_actions(self, observation, computed_actions):
        reversed_computed_actions = computed_actions.copy()
        reversed_computed_actions.reverse()
        test_obs = observation
        actions_valid = True
        for action in reversed_computed_actions:
            if action == 0:
                continue
            avaliable_actions = self.model.ACTIONS(test_obs)
            if action not in avaliable_actions:
                actions_valid = False
                break
            test_obs = self.model.RESULT(test_obs, action)
        return actions_valid

    def agent_function(self, observation):
        if len(self.actions) == 0:
            logging.info("--------------------------------    Calculating Search...  ---------------------------------")
            
            score = observation['score']
            num_moves = observation['num_moves']
            
            if num_moves > 50 and score < num_moves + 50:
                self.actions = [0, 0, 0, 0, 0, 0, 0]
            else:
                self.custom_search(observation)
                
                if len(self.actions) != 0:
                    logging.info(f"Actions: {self.actions}")
                    logging.info("--------------------------------    Search Calculated  ---------------------------------")
                else:
                    logging.info("No Actions Found")
                    logging.info(f"Actions: {self.actions}")
                    logging.info("--------------------------------    Search Failed  ---------------------------------")
                    raise Exception("No Actions Found")
        
        action = self.actions.pop()
        return action