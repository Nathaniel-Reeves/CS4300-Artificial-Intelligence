#!/usr/bin/env python3
import logging
import random

ACTION_UP = 0
ACTION_RIGHT = 1
ACTION_DOWN = 2
ACTION_LEFT = 3
ALL_ACTIONS = [ACTION_UP, ACTION_RIGHT, ACTION_DOWN, ACTION_LEFT]

NEIGHBORS_ALL_ROWS = 0
NEIGHBORS_NEXT_ROW = 1

def wait(dev_mode=0):
    if dev_mode:
        print()
        input("Press Enter to continue...")
        print()
        print()
    return

class Policy:
    
    def __init__(self):
        self.num_states = 4
        self.size = 37
        self.rows = 4
        self.cols = 12
        self.policy = [0 for i in range(self.size)]
    
    def randomize(self):
        for i in range(self.size):
            self.policy[i] = random.choice(ALL_ACTIONS)
        return
    
    def set_policy(self, policy):
        self.policy = policy
    
    def get_action(self, state):
        return self.policy[state]
    
    def copy_policy_array(self):
        return self.policy.copy()
    
    def get_policy(self):
        return self.policy
    
    def _translate_action(self, action):
        if action == 0:
            return 'U'
        elif action == 1:
            return 'R'
        elif action == 2:
            return 'D'
        elif action == 3:
            return 'L'
    
    def __str__(self):
        out = '\n'
        for i in range(self.rows):
            for j in range(self.cols):
                if (i*self.cols + j) >= self.size:
                    out += '   '
                    continue
                # out += str(i*self.cols + j) + ' '
                out += ' ' + self._translate_action(self.policy[i*self.cols + j]) + ' '
            out += '\n'
        
        out += '\n'
        for i in range(self.rows):
            for j in range(self.cols):
                if (i*self.cols + j) >= self.size:
                    out += '   '
                    continue
                out += str(i*self.cols + j).zfill(2) + ' '
            out += '\n'
        return out

class CliffWalkingModel:
    
    def __init__(self, env):
        self._env = env
        self.size = 37
        self.num_states = 4
        self._neighbor_mode = NEIGHBORS_ALL_ROWS
        return
    
    def set_neighbors_all_rows(self):
        self._neighbor_mode = NEIGHBORS_ALL_ROWS
        return
    
    def set_neighbors_next_row(self):
        self._neighbor_mode = NEIGHBORS_NEXT_ROW
        return
    
    def _neighbors_all_rows(self, policy):
        neighbours = []
        for i in range(self.size):
            for j in range(self.num_states):
                neighbour_policy = policy.copy_policy_array()
                neighbour_policy[i] = j
                new_policy = Policy()
                new_policy.set_policy(neighbour_policy)
                neighbours.append(new_policy)
        return neighbours
    
    def _neighbors_next_row(self, policy):
        neighbours = []
        for i in range(self.size):
            neighbour_policy = policy.copy_policy_array()
            neighbour_policy[i] = (neighbour_policy[i] + 1) % self.num_states
            new_policy = Policy()
            new_policy.set_policy(neighbour_policy)
            neighbours.append(new_policy)
            
            neighbour_policy = policy.copy_policy_array()
            neighbour_policy[i] = (neighbour_policy[i] - 1) % self.num_states
            new_policy = Policy()
            new_policy.set_policy(neighbour_policy)
            neighbours.append(new_policy)
        return neighbours
    
    def UTILITY(self, policy):
        logging.debug('---------------------Calling UTILITY')
        logging.debug(f"Testing Policy: {policy}")
        total_utility = 0
        self._env.reset()
        start_state = self._env.unwrapped.s
        truncated = False
        terminated = False
        for state_position in range(self.size-1, 0, -1):
            logging.debug(f"Starting State: {state_position}")
            steps_taken = 1
            self._env.unwrapped.s = state_position
            next_state = state_position
            while True:
                action = policy.get_action(next_state)
                next_state, reward, terminated, truncated, debug = self._env.step(action)
                steps_taken += 1
                if truncated: # goes over time limit
                    break
                if terminated: # walker made it to goal
                    break
            total_utility += steps_taken
            self._env.reset()

        self._env.unwrapped.s = start_state
        logging.debug(f"Utility: {total_utility}")
        logging.debug('---------------------End UTILITY \n\n')
        wait()
        return total_utility
    
    def NEIGHBORS(self, policy):
        logging.debug('---------------------Calling NEIGHBORS')
        logging.debug(f"Policy: {policy}")
        if self._neighbor_mode == NEIGHBORS_ALL_ROWS:
            logging.debug(f"Neighbors Mode: All Rows")
            neighbours = self._neighbors_all_rows(policy)
        elif self._neighbor_mode == NEIGHBORS_NEXT_ROW:
            logging.debug(f"Neighbors Mode: Next Row")
            neighbours = self._neighbors_next_row(policy)
        else:
            raise Exception(f"Unknown neighbors mode: {self._neighbor_mode}")
        logging.debug(f"Num Neighbours: {len(neighbours)}")
        logging.debug('---------------------End NEIGHBORS \n\n')
        wait()
        return neighbours
    
    def RANDOM_POLICY(self):
        logging.debug('---------------------Calling RANDOM_STATE')
        policy = Policy()
        policy.randomize()
        logging.debug(f"Random Policy: {policy}")
        logging.debug('---------------------End RANDOM_STATE \n\n')
        wait()
        return policy