#!/usr/bin/env python3

class PolicyAgent:
    
    def __init__(self, policy):
        self.policy = policy
        
    def reset(self):
        return
    
    def agent_function(self, state):
        # Where state is a integer representing the current location of the agent.
        return self.policy[state]
        