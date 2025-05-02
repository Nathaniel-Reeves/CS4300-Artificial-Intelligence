#!/usr/bin/env python3

import spider_solitare
import random

class HumanAgent:
    
    def __init__(self):
        """required method"""
        self.model = spider_solitare.SpiderSolitareModel()
        return
    
    def reset(self):
        """required method"""
        return

    def agent_function(self, observation):
        actions = self.model.ACTIONS(observation)
        
        print("Choose an action:", end="  ")
        for i, action in enumerate(actions):
            print(f"{action}", end="  ")
        print()
        
        while True:
            try:
                action = int(input("Enter the number of the action you would like to take: "))
                if action not in actions:
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter the number of the action you would like to take.")
            
        return action