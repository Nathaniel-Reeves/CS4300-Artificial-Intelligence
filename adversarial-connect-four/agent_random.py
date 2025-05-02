#!/usr/bin/env python3

import numpy as np
import time
import logging

class AgentRandom:
    
    def __init__(self):
        """Required Method"""
        return
    
    def reset(self):
        """Required Method"""
        return
    
    def agent_function(self, observation, agent):
        """Required Method"""
        action = np.random.choice(np.where(observation['action_mask'])[0])
        logging.info(f"RANDOM ACTION: {action}")
        return action
