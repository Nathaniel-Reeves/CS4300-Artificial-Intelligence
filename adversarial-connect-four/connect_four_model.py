#!/usr/bin/env python3
from __future__ import annotations
import logging

class ConnectFourModel:

    def __init__(self):
        """Required Method"""
        return

    def reset(self):
        """Required Method"""
        return
    
    def print_state(self, state, agent=None):
        # logging.debug("------ PRINTING STATE ------")
        
        print()
        print('Agent: ', agent)
        print()
        print('  0     1     2     3     4     5     6')
        for row in state['observation']:
            for col in row:
                print(col, end=" ")
            print()
        print()
        
        # logging.debug("-----------------------------\n")
        return
    
    def ACTIONS(self, state):
        """Get all possible actions from the current state."""
        logging.debug("------ CALLING ACTIONS ------")
        
        default_actions = [0, 1, 2, 3, 4, 5, 6]
        column_count = [0, 0, 0, 0, 0, 0, 0]
        
        for row in state['observation']:
            for i, col in enumerate(row):
                column_count[i] += col[0] + col[1]
        
        for i, count in enumerate(column_count):
            if (count == 6):
                default_actions.remove(i)
        
        logging.debug(f"Avaliable Actions: {default_actions}")
        logging.info(f"Avaliable Actions: {default_actions}")
        logging.debug("-----------------------------\n")
        return default_actions
    
    def flip_state(self, state):
        """Flip the state for the opponent."""
        logging.debug("------ CALLING FLIP_STATE ------")
        
        logging.debug("Current State:")
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            self.print_state(state)
        
        flipped_state = state.copy()
        
        for i, row in enumerate(flipped_state['observation']):
            for j, col in enumerate(row):
                flipped_state['observation'][i][j] = col[::-1]
        
        logging.debug("Flipped State:")
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            self.print_state(flipped_state)
        
        logging.debug("-----------------------------\n")
        return flipped_state
    
    def RESULT(self, state, action, agent=None):
        """Generate the new state by applying the action to the current state."""
        logging.debug("------ CALLING RESULT ------")
        new_state = state.copy()
        
        logging.debug("Current State:")
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            self.print_state(state, agent)
        logging.debug(f"Taking Action: {action}")
        
        for i, row in enumerate(new_state['observation']):
            if sum(row[action]) == 1:
                new_state['observation'][i-1][action] = [1, 0]
                break
            if i == 5:
                new_state['observation'][i][action] = [1, 0]
        
        logging.debug("New State:")
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            self.print_state(new_state, agent)
        
        logging.debug("-----------------------------\n")
        return self.flip_state(new_state)
        # return new_state
    
    def LOOSE_TEST(self, state):
        """Test if the current state is a loose state."""
        logging.debug("------ CALLING LOOSE_TEST ------")
        
        win = False
        
        # Loose Test Horizontal Wins
        for mask in self.horizontal_mask():
            for i in range(4):
                if state['observation'][mask[i][0]][mask[i][1]][0]:
                    break
                if i == 3:
                    win = True
            if win:
                break
        
        # Loose Test Vertical Wins
        if win is False:
            for mask in self.vertical_mask():
                for i in range(4):
                    if state['observation'][mask[i][0]][mask[i][1]][0]:
                        break
                    if i == 3:
                        win = True
                if win:
                    break
        
        # Loose Test Right Diagonal Wins
        if win is False:
            for mask in self.right_diagonal_mask():
                for i in range(4):
                    if state['observation'][mask[i][0]][mask[i][1]][0]:
                        break
                    if i == 3:
                        win = True
                if win:
                    break
        
        # Loose Test Left Diagonal Wins
        if win is False:
            for mask in self.left_diagonal_mask():
                for i in range(4):
                    if state['observation'][mask[i][0]][mask[i][1]][0]:
                        break
                    if i == 3:
                        win = True
                if win:
                    break
        
        logging.debug(f"Loose Found Status: {win}")
        logging.debug("-----------------------------\n")
        return win
    
    def WIN_TEST(self, state):
        """Test if the current state is a win state."""
        logging.debug("------ CALLING WIN_TEST ------")
        
        win = False
        
        # Goal Test Horizontal Wins
        for mask in self.horizontal_mask():
            for i in range(4):
                if state['observation'][mask[i][0]][mask[i][1]][1]:
                    break
                if i == 3:
                    win = True
            if win:
                break
        
        # Goal Test Vertical Wins
        if win is False:
            for mask in self.vertical_mask():
                for i in range(4):
                    if state['observation'][mask[i][0]][mask[i][1]][1]:
                        break
                    if i == 3:
                        win = True
                if win:
                    break
        
        # Goal Test Right Diagonal Wins
        if win is False:
            for mask in self.right_diagonal_mask():
                for i in range(4):
                    if state['observation'][mask[i][0]][mask[i][1]][1]:
                        break
                    if i == 3:
                        win = True
                if win:
                    break
        
        # Goal Test Left Diagonal Wins
        if win is False:
            for mask in self.left_diagonal_mask():
                for i in range(4):
                    if state['observation'][mask[i][0]][mask[i][1]][1]:
                        break
                    if i == 3:
                        win = True
                if win:
                    break
        
        logging.debug(f"Goal Found Status: {win}")
        logging.debug("-----------------------------\n")
        return win
    
    def EVALUATE(self, state):
        """Evaluate the current state if it is a goal state."""
        logging.debug("------ CALLING EVALUATE ------")
        
        loose = self.LOOSE_TEST(state)
        
        if loose:
            logging.debug("Loose Found")
            logging.debug("-----------------------------\n")
            return -100000
        
        win = self.WIN_TEST(state)
        
        if win:
            logging.debug("Win Found")
            logging.debug("-----------------------------\n")
            return 100000
        
        reward = 1
        penalty = -10
        
        # Evaluate Horizontal
        horizontal_score = self.evaluate_mask(self.horizontal_mask(), state, reward, penalty)
        
        # Evaluate Vertical
        vertical_score = self.evaluate_mask(self.vertical_mask(), state, reward, penalty)
        
        # Evaluate Right Diagonal
        right_diagonal_score = self.evaluate_mask(self.right_diagonal_mask(), state, reward, penalty)
        
        # Evaluate Left Diagonal
        left_diagonal_score = self.evaluate_mask(self.left_diagonal_mask(), state, reward, penalty)
        
        total_score = horizontal_score + vertical_score + right_diagonal_score + left_diagonal_score
        
        logging.debug(f"Total Score: {total_score}")
        logging.debug("-----------------------------\n")
        return total_score
    
    def evaluate_mask(self, masks, state, eval_reward, eval_penalty):
        score = 0
        
        # Player Wins
        for mask in masks:
            num_cells_filled = 0
            for i in range(4):
                # If there are three cells filled by the player, player gets reward
                if state['observation'][mask[i][0]][mask[i][1]][1]:
                    num_cells_filled += 1
                # If there is a cell filled by the opponent, player is not rewarded
                if state['observation'][mask[i][0]][mask[i][1]][0]:
                    num_cells_filled = -10
            if num_cells_filled >= 2:
                score += eval_reward
        
        # Opponent Wins
        for mask in masks:
            num_cells_filled = 0
            for i in range(4):
                # If there are three cells filled by the opponent, player gets penalty
                if state['observation'][mask[i][0]][mask[i][1]][0]:
                    num_cells_filled += 1
                # If there is a cell filled by the player, player is not penalized
                if state['observation'][mask[i][0]][mask[i][1]][1]:
                    num_cells_filled = -10
            if num_cells_filled >= 2:
                score += eval_penalty
        return score
    
    def horizontal_mask(self):
        """returns all groups of row col pairs that represent the horizontal mask"""
        mask = [
            [(0, 0), (0, 1), (0, 2), (0, 3)],
            [(0, 1), (0, 2), (0, 3), (0, 4)],
            [(0, 2), (0, 3), (0, 4), (0, 5)],
            [(0, 3), (0, 4), (0, 5), (0, 6)],
            
            [(1, 0), (1, 1), (1, 2), (1, 3)],
            [(1, 1), (1, 2), (1, 3), (1, 4)],
            [(1, 2), (1, 3), (1, 4), (1, 5)],
            [(1, 3), (1, 4), (1, 5), (1, 6)],
            
            [(2, 0), (2, 1), (2, 2), (2, 3)],
            [(2, 1), (2, 2), (2, 3), (2, 4)],
            [(2, 2), (2, 3), (2, 4), (2, 5)],
            [(2, 3), (2, 4), (2, 5), (2, 6)],
            
            [(3, 0), (3, 1), (3, 2), (3, 3)],
            [(3, 1), (3, 2), (3, 3), (3, 4)],
            [(3, 2), (3, 3), (3, 4), (3, 5)],
            [(3, 3), (3, 4), (3, 5), (3, 6)],
            
            [(4, 0), (4, 1), (4, 2), (4, 3)],
            [(4, 1), (4, 2), (4, 3), (4, 4)],
            [(4, 2), (4, 3), (4, 4), (4, 5)],
            [(4, 3), (4, 4), (4, 5), (4, 6)],
            
            [(5, 0), (5, 1), (5, 2), (5, 3)],
            [(5, 1), (5, 2), (5, 3), (5, 4)],
            [(5, 2), (5, 3), (5, 4), (5, 5)],
            [(5, 3), (5, 4), (5, 5), (5, 6)],
        ]
        return mask
    
    def vertical_mask(self):
        """returns all groups of row col pairs that represent the vertical mask"""
        mask = [
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            [(1, 0), (2, 0), (3, 0), (4, 0)],
            [(2, 0), (3, 0), (4, 0), (5, 0)],
            
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(1, 1), (2, 1), (3, 1), (4, 1)],
            [(2, 1), (3, 1), (4, 1), (5, 1)],
            
            [(0, 2), (1, 2), (2, 2), (3, 2)],
            [(1, 2), (2, 2), (3, 2), (4, 2)],
            [(2, 2), (3, 2), (4, 2), (5, 2)],
            
            [(0, 3), (1, 3), (2, 3), (3, 3)],
            [(1, 3), (2, 3), (3, 3), (4, 3)],
            [(2, 3), (3, 3), (4, 3), (5, 3)],
            
            [(0, 4), (1, 4), (2, 4), (3, 4)],
            [(1, 4), (2, 4), (3, 4), (4, 4)],
            [(2, 4), (3, 4), (4, 4), (5, 4)],
            
            [(0, 5), (1, 5), (2, 5), (3, 5)],
            [(1, 5), (2, 5), (3, 5), (4, 5)],
            [(2, 5), (3, 5), (4, 5), (5, 5)],
            
            [(0, 6), (1, 6), (2, 6), (3, 6)],
            [(1, 6), (2, 6), (3, 6), (4, 6)],
            [(2, 6), (3, 6), (4, 6), (5, 6)],
        ]
        return mask
    
    def right_diagonal_mask(self):
        """returns all groups of row col pairs that represent the right diagonal mask"""
        mask = [
            [(3, 0), (2, 1), (1, 2), (0, 3)],
            [(3, 1), (2, 2), (1, 3), (0, 4)],
            [(3, 2), (2, 3), (1, 4), (0, 5)],
            [(3, 3), (2, 4), (1, 5), (0, 6)],
            
            [(4, 0), (3, 1), (2, 2), (1, 3)],
            [(4, 1), (3, 2), (2, 3), (1, 4)],
            [(4, 2), (3, 3), (2, 4), (1, 5)],
            [(4, 3), (3, 4), (2, 5), (1, 6)],
            
            [(5, 0), (4, 1), (3, 2), (2, 3)],
            [(5, 1), (4, 2), (3, 3), (2, 4)],
            [(5, 2), (4, 3), (3, 4), (2, 5)],
            [(5, 3), (4, 4), (3, 5), (2, 6)],
        ]
        return mask
    
    def left_diagonal_mask(self):
        """returns all groups of row col pairs that represent the left diagonal mask"""
        mask = [
            [(0, 0), (1, 1), (2, 2), (3, 3)],
            [(0, 1), (1, 2), (2, 3), (3, 4)],
            [(0, 2), (1, 3), (2, 4), (3, 5)],
            [(0, 3), (1, 4), (2, 5), (3, 6)],
            
            [(1, 0), (2, 1), (3, 2), (4, 3)],
            [(1, 1), (2, 2), (3, 3), (4, 4)],
            [(1, 2), (2, 3), (3, 4), (4, 5)],
            [(1, 3), (2, 4), (3, 5), (4, 6)],
            
            [(2, 0), (3, 1), (4, 2), (5, 3)],
            [(2, 1), (3, 2), (4, 3), (5, 4)],
            [(2, 2), (3, 3), (4, 4), (5, 5)],
            [(2, 3), (3, 4), (4, 5), (5, 6)],
        ]
        return mask
