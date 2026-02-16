#!/usr/bin/env python3

import marble_solitare
from marble_solitare.envs.marble_solitare_model import MarbleSolitareModel
import hashlib
import threading

class DFSAgent:
    """Agent that uses Depth-First Search to find a solution."""
    
    def __init__(self, visualize=False):
        """Initialize the DFS agent.
        
        Args:
            visualize: If True, search until user presses Enter, then replay best solution
        """
        self.model = MarbleSolitareModel()
        self.solution_path = []
        self.current_step = 0
        self.visualize = visualize
        self.search_interrupted = False
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
    
    def _dfs_search(self, initial_observation, max_depth=100):
        """Perform DFS to find a solution.
        
        Args:
            initial_observation: Starting observation
            max_depth: Maximum search depth to prevent infinite loops
            
        Returns:
            List of actions to reach goal, or empty list if no solution
        """
        print("Starting DFS search for a solution...")
        print(f"Max depth: {max_depth}")
        if self.visualize:
            print("\n*** VISUALIZATION MODE ***")
            print("DFS will search until you press Enter...")
            print("Then the best solution found will be replayed move-by-move.\n")
            
            # Start a thread to wait for user input
            self.user_stop = False
            def wait_for_enter():
                input()
                self.user_stop = True
            input_thread = threading.Thread(target=wait_for_enter, daemon=True)
            input_thread.start()
        
        self.nodes_explored = 0
        self.best_solution = []
        self.best_marbles = float('inf')
        self.search_interrupted = False
        
        def dfs_recursive(current_obs, path, visited, depth):
            """Recursive DFS helper."""
            # Check for user interrupt first (before incrementing counter)
            if self.visualize and self.user_stop and not self.search_interrupted:
                self.search_interrupted = True
                print(f"\n{'='*60}")
                print(f"Search interrupted by user after {self.nodes_explored} nodes.")
                print(f"{'='*60}")
                return "INTERRUPTED"  # Special return value to stop all recursion
            
            # If we've already interrupted, propagate it up
            if self.search_interrupted:
                return "INTERRUPTED"
            
            self.nodes_explored += 1
            
            # Print progress updates
            if self.nodes_explored % 1000 == 0:
                print(f"Explored {self.nodes_explored} nodes, depth: {depth}, marbles: {current_obs['marbles_left']}, best: {self.best_marbles}")
            
            # Check if we reached the goal
            if self.model.GOAL_TEST(current_obs):
                print(f"\n*** Solution found! Explored {self.nodes_explored} nodes.")
                print(f"Solution length: {len(path)} moves")
                print(f"Final marbles: {current_obs['marbles_left']}")
                return path
            
            # Track best solution so far (fewest marbles)
            if current_obs['marbles_left'] < self.best_marbles:
                self.best_marbles = current_obs['marbles_left']
                self.best_solution = path.copy()
            
            # Check depth limit
            if depth >= max_depth:
                return None
            
            # Try all possible actions
            actions = self.model.ACTIONS(current_obs)
            
            # If no actions available, this is a dead end
            if not actions:
                return None
            
            for action in actions:
                # Get resulting state
                next_obs = self.model.RESULT(current_obs, action)
                obs_key = self._observation_to_key(next_obs)
                
                # Only explore if not visited in this path
                if obs_key not in visited:
                    visited.add(obs_key)
                    result = dfs_recursive(next_obs, path + [action], visited, depth + 1)
                    visited.remove(obs_key)  # Backtrack
                    
                    # Propagate interrupt signal
                    if result == "INTERRUPTED":
                        return "INTERRUPTED"
                    
                    if result is not None:
                        return result
            
            return None
        
        # Start DFS
        visited = set()
        visited.add(self._observation_to_key(initial_observation))
        result = dfs_recursive(initial_observation, [], visited, 0)
        
        # Handle interrupt signal
        if result == "INTERRUPTED":
            result = None
        
        if result is None:
            if self.search_interrupted and self.visualize:
                print(f"\n{'='*60}")
                print(f"SEARCH SUMMARY")
                print(f"{'='*60}")
                print(f"Nodes explored: {self.nodes_explored}")
                if self.best_solution:
                    print(f"Best solution found: {len(self.best_solution)} moves")
                    print(f"Ending with {self.best_marbles} marbles remaining")
                    print(f"\n>>> Now replaying the best solution move-by-move...")
                    print(f"{'='*60}\n")
                    return self.best_solution
                else:
                    print("No solution found.")
                    return []
            else:
                print(f"\nNo complete solution found after exploring {self.nodes_explored} nodes.")
                if self.best_solution:
                    print(f"Best partial solution found: {len(self.best_solution)} moves, {self.best_marbles} marbles remaining")
                return []
        
        return result
    
    def agent_function(self, observation):
        """Return the next action to take.
        
        On first call, computes a solution path using DFS.
        On subsequent calls, returns the next action from the solution.
        
        Args:
            observation: Current observation
            
        Returns:
            Action tuple (from_y, from_x, to_y, to_x) or None
        """
        # If we haven't computed the solution yet, do DFS
        if not self.solution_path:
            if not self.visualize:
                print("\nComputing solution using DFS...")
                print("This will search depth-first for a winning path...")
            self.solution_path = self._dfs_search(observation, max_depth=50)
            self.current_step = 0
            
            if not self.solution_path:
                print("No solution found!")
                return None
            
            if not self.visualize:
                print(f"\nSolution computed: {len(self.solution_path)} moves")
                print("\nPress Enter to execute solution step by step...")
        
        # Return next action from solution
        if self.current_step < len(self.solution_path):
            action = self.solution_path[self.current_step]
            self.current_step += 1
            if self.visualize:
                print(f"\n>>> Move {self.current_step}/{len(self.solution_path)}: from ({action[0]},{action[1]}) to ({action[2]},{action[3]})")
            else:
                print(f"Step {self.current_step}/{len(self.solution_path)}: Move from ({action[0]},{action[1]}) to ({action[2]},{action[3]})")
            return action
        
        # Solution playback complete
        if self.visualize and self.current_step == len(self.solution_path):
            print(f"\n{'='*60}")
            print(f"VISUALIZATION COMPLETE")
            print(f"{'='*60}")
            print(f"Replayed {len(self.solution_path)} moves")
            print(f"{'='*60}\n")
        
        # No more actions
        return None
