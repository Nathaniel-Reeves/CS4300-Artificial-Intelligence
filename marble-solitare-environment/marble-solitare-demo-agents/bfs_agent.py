#!/usr/bin/env python3

import marble_solitare
from marble_solitare.envs.marble_solitare_model import MarbleSolitareModel
from collections import deque
import hashlib
import json

class BFSAgent:
    """Agent that uses Breadth-First Search to find the optimal solution."""
    
    def __init__(self):
        """Initialize the BFS agent."""
        self.model = MarbleSolitareModel()
        self.solution_path = []
        self.current_step = 0
        return
    
    def reset(self):
        """Reset the agent for a new episode."""
        self.solution_path = []
        self.current_step = 0
        return
    
    def _observation_to_key(self, observation):
        """Convert observation to a hashable key for visited set.
        
        Args:
            observation: Dict with 'board', 'marbles_left', 'moves_made'
            
        Returns:
            String hash of the board state
        """
        # Convert board to bytes and hash it
        board_bytes = observation['board'].tobytes()
        return hashlib.md5(board_bytes).hexdigest()
    
    def _bfs_search(self, initial_observation):
        """Perform BFS to find shortest path to goal.
        
        Args:
            initial_observation: Starting observation
            
        Returns:
            List of actions to reach goal, or empty list if no solution
        """
        print("Starting BFS search for optimal solution...")
        
        # Queue stores: (observation, path_to_reach_it)
        queue = deque([(initial_observation, [])])
        visited = set()
        visited.add(self._observation_to_key(initial_observation))
        
        nodes_explored = 0
        
        while queue:
            current_obs, path = queue.popleft()
            nodes_explored += 1
            
            if nodes_explored % 1000 == 0:
                print(f"Explored {nodes_explored} nodes, queue size: {len(queue)}, marbles: {current_obs['marbles_left']}")
            
            # Check if we reached the goal
            if self.model.GOAL_TEST(current_obs):
                print(f"\nSolution found! Explored {nodes_explored} nodes.")
                print(f"Solution length: {len(path)} moves")
                print(f"Final marbles: {current_obs['marbles_left']}")
                return path
            
            # Try all possible actions
            actions = self.model.ACTIONS(current_obs)
            
            for action in actions:
                # Get resulting state
                next_obs = self.model.RESULT(current_obs, action)
                obs_key = self._observation_to_key(next_obs)
                
                # Only explore if not visited
                if obs_key not in visited:
                    visited.add(obs_key)
                    new_path = path + [action]
                    queue.append((next_obs, new_path))
        
        print(f"\nNo solution found after exploring {nodes_explored} nodes.")
        return []
    
    def agent_function(self, observation):
        """Return the next action to take.
        
        On first call, computes the full solution path using BFS.
        On subsequent calls, returns the next action from the solution.
        
        Args:
            observation: Current observation
            
        Returns:
            Action tuple (from_y, from_x, to_y, to_x) or None
        """
        # If we haven't computed the solution yet, do BFS
        if not self.solution_path:
            print("\nComputing optimal solution using BFS...")
            print("This may take a while for complex positions...")
            self.solution_path = self._bfs_search(observation)
            self.current_step = 0
            
            if not self.solution_path:
                print("No solution exists from this position!")
                return None
            
            print(f"\nSolution computed: {len(self.solution_path)} moves")
            print("\nPress Enter to execute solution step by step...")
        
        # Return next action from solution
        if self.current_step < len(self.solution_path):
            action = self.solution_path[self.current_step]
            self.current_step += 1
            print(f"Step {self.current_step}/{len(self.solution_path)}: Move from ({action[0]},{action[1]}) to ({action[2]},{action[3]})")
            return action
        
        # No more actions
        return None
