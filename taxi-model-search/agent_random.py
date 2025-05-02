#!/usr/bin/env python3

import random
import taxi_model as taxi

class AgentRandom:

    def __init__(self):
        """required method"""
        self.model = taxi.TaxiDrivingModel()
        return

    def reset(self):
        """required method"""
        self.model.reset()
        return

    def agent_function(self, state):
        """required method"""
        self.model.decode_state(state)
        action = random.choice(taxi.ALL_ACTIONS)
        return action