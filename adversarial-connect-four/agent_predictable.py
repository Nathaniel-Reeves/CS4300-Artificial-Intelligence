#!/usr/bin/env python3

import numpy as np
import logging
from connect_four_model import ConnectFourModel

class AgentPredictable:
    
    def __init__(self):
        """Required Method"""
        self.cutoff_depth = 38
        self.model = ConnectFourModel()
        return
    
    def reset(self):
        """Required Method"""
        self.cutoff_depth = 38
        self.model.reset()
        return
    
    def agent_function(self, observation, agent):
        action = self.MINIMAX(observation)
        if action is None:
            # If the action is None, then choose a random avalible action
            action_mask = observation['action_mask']
            action = np.random.choice(np.where(action_mask == 1)[0])
        return action
    
    def MINIMAX(self, initial_state):
        alpha = float('-inf')
        beta = float('inf')
        best_value = float('-inf')
        best_action = None
        depth = 0
        for action in self.model.ACTIONS(initial_state):
            next_state = self.model.RESULT(initial_state, action)
            value = self.MIN(next_state, depth+1, alpha, beta)
            if value > best_value:
                best_value = value
                best_action = action
                if best_value > beta:
                    return best_value
                if best_value > alpha:
                    alpha = best_value
        logging.info(f"Best Action: {best_action}")
        logging.info(f"Best Value: {best_value}")
        return best_action
    
    def MAX(self, current_state, depth, alpha, beta):
        if depth >= self.cutoff_depth or self.model.WIN_TEST(current_state):
            return self.model.EVALUATE(current_state)
        best_value = float('-inf')
        
        actions = self.model.ACTIONS(current_state)
        if len(actions) == 0:
            return best_value
        
        for action in actions:
            next_state = self.model.RESULT(current_state, action)
            value = self.MIN(next_state, depth+1, alpha, beta)
            if value > best_value:
                best_value = value
                if best_value > beta:
                    return best_value
                if best_value > alpha:
                    alpha = best_value
        return best_value
    
    def MIN(self, current_state, depth, alpha, beta):
        if depth >= self.cutoff_depth or self.model.WIN_TEST(current_state):
            return self.model.EVALUATE(current_state)
        best_value = float('inf')
        
        actions = self.model.ACTIONS(current_state)
        if len(actions) == 0:
            return best_value
        
        for action in actions:
            next_state = self.model.RESULT(current_state, action)
            value = self.MAX(next_state, depth+1, alpha, beta)
            if value < best_value:
                best_value = value
                if best_value < alpha:
                    return best_value
                if best_value < beta:
                    beta = best_value
        return best_value
