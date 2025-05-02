#!/usr/bin/env python3

import random
import cliff_model as cliff

class AgentRandom:

    def __init__(self):
        """required method"""
        self.model = cliff.CliffWalkingModel()
        return

    def reset(self):
        """required method"""
        self.model.reset()
        return

    def agent_function(self, state):
        """required method"""
        action = random.choice(cliff.ALL_ACTIONS)
        return action