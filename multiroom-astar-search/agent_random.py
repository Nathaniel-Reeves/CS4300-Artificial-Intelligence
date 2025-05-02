#!/usr/bin/env python3

import random
import minigrid_model as mgrid

class AgentRandom:

    def __init__(self):
        """required method"""
        self.model = mgrid.MiniGridModel()
        return

    def reset(self):
        """required method"""
        self.model.reset()
        return

    def agent_function(self, state):
        """required method"""
        self.model.decode_state(state)
        action = random.choice(mgrid.ALL_ACTIONS)
        return action