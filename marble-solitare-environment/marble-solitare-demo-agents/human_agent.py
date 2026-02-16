#!/usr/bin/env python3

import marble_solitare
from marble_solitare.envs.marble_solitare_model import MarbleSolitareModel

class HumanAgent:
    
    def __init__(self):
        """required method"""
        self.model = MarbleSolitareModel()
        return
    
    def reset(self):
        """required method"""
        return

    def agent_function(self, observation):
        actions = self.model.ACTIONS(observation)
        
        if not actions:
            print("No valid actions available!")
            return None
        
        print("\nAvailable actions (from_y, from_x, to_y, to_x):")
        for i, action in enumerate(actions):
            print(f"  {i}: {action}")
        print()
        
        while True:
            try:
                choice = int(input("Enter the number of the action you would like to take: "))
                if choice < 0 or choice >= len(actions):
                    raise ValueError
                action = actions[choice]
                break
            except ValueError:
                print(f"Invalid input. Please enter a number between 0 and {len(actions) - 1}.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                return None
            
        return action