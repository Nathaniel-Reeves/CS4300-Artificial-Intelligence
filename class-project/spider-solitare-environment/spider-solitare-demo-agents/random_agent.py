#!/usr/bin/env python3

import spider_solitare
import random

class RandomAgent:
    
    def __init__(self):
        """required method"""
        self.model = spider_solitare.SpiderSolitareModel()
        return
    
    def reset(self):
        """required method"""
        return

    def agent_function(self, observation):
        actions = self.model.ACTIONS(observation)
        action = random.choice(actions)
        return action