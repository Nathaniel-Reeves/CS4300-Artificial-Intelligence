#!/usr/bin/env python3

import numpy as np
import time
from connect_four_model import ConnectFourModel
import logging

class AgentHuman:
    
    def __init__(self):
        """Required Method"""
        self.model = ConnectFourModel()
        return
    
    def reset(self):
        """Required Method"""
        return
    
    def agent_function(self, observation, agent):
        """Required Method"""
        logging.debug("------ CALLING HUMAN AGENT_FUNCTION ------")
        logging.debug(f"ACTING AS AGENT: {agent}")
        
        
        action = int(input("Enter the column number (0-6): "))
        
        
        logging.debug("-----------------------------\n")
        return action
