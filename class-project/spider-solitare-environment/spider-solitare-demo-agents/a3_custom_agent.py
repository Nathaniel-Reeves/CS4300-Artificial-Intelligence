#!/usr/bin/env python3

import spider_solitare
import logging
import random

class PickupNode:
    
    def __init__(self):
        self.parent_node = None
        self.action = None
        self.observation = None
        self.depth = 0

class PutdownNode:
    
    def __init__(self):
        self.parent_node = None
        self.action = None
        self.observation = None
        self.score = float('-inf')
        self.depth = 0
        self.goal = False
    
    def __lt__(self, other):
        return self.score < other.score
    
    def __eq__(self, other):
        return self.score == other.score
    
    def __gt__(self, other):
        return self.score > other.score
    
    def __le__(self, other):
        return self.score <= other.score
    
    def __ge__(self, other):
        return self.score >= other.score

class ThreeCustomAgent:
    
    def __init__(self):
        """required method"""
        self.model = spider_solitare.SpiderSolitareModel()
        self.max_depth = 14
        self.actions = []
        self.num_piles = 0
        self.putdown_nodes = []
        self.bad_search_counter = 0
        self.bad_search_limit = 10
        return
    
    def reset(self):
        """required method"""
        self.model = spider_solitare.SpiderSolitareModel()
        self.max_depth = 14
        self.actions = []
        self.num_piles = 0
        self.putdown_nodes = []
        self.bad_search_counter = 0
        self.score_before_bad_search = 0
        self.bad_search_limit = 10
        return
    
    def calc_bonus(self, observation):
        
        piles = observation['piles']
        score = 0
        
        # If there are 4 or more completed sets, calculate penalty
        # completed_suits = []
        # num_completed_suits = 0
        # completed_suits = observation['completed_suits'].values()
        # for suit in completed_suits:
        #     if len(suit) == 13:
        #         num_completed_suits += 1
        # if num_completed_suits >= 5:
        #     # Penalty for every in the game that is not in a completed set
        #     for pile in piles.values():
        #         for card in pile:
        #             score -= 10
        #     return score

        for pile in piles.values():
            
             # if the pile is empty, set penalty and continue
            if len(pile) == 0:
                score -= 10
                continue
            
            # Reverse the pile
            reverse_pile = list(pile).copy()
            reverse_pile.reverse()
            
            streak = 0
            streak_value = 0
            bonus = 0
            has_face_down_card = False
            has_king = False
            streaks = []

            for index, card in enumerate(reverse_pile):
                
                # If the card is face down, flag and skip
                if card[2] == 0:
                    has_face_down_card = True
                    continue
                
                if card[0] == 13:
                    has_king = True
                
                # If there is no next card, break
                next_card = reverse_pile[index + 1] if len(reverse_pile) > index + 1 else None
                if next_card is None:
                    break
                
                
                # If the card is one less rank than the next card and the same suit, increment the streak
                if card[1] == next_card[1] and card[0] == next_card[0] + 1:
                    streak += 1
                    streak_value += card[0]
                else:
                    # If the streak is greater than 1, calculate the bonus
                    if streak > 1:
                        bonus = streak_value * streak
                        streaks.append(bonus)
                        
                    streak = 0
                    streak_value = 0
                    bonus = 0
            
            # If all cards in the pile are face up, double the bonus
            if not has_face_down_card and not has_king:
                for bonus in streaks:
                    bonus = bonus * 2
                score += bonus
        
        return score
    
    def HANDLE_PICKUP_NODE(self, node):
        # Unpack Node
        action = node.action
        observation = node.observation
        depth = node.depth
        
        if depth == self.max_depth:
            return
        
        actions = self.model.ACTIONS(observation)
        
        for action in actions:
            if action == 0:
                continue
            if action > 0 and action <= self.num_piles:
                new_node = PickupNode()
                new_node.action = action
                new_node.observation = self.model.RESULT(observation, action)
                new_node.depth = depth + 1
                new_node.parent_node = node
                self.HANDLE_PICKUP_NODE(new_node)
            if action > self.num_piles:
                new_node = PutdownNode()
                new_node.action = action
                new_node.observation = self.model.RESULT(observation, action)
                new_node.parent_node = node
                
                score = self.model.EVALUATE(new_node.observation)
                bonus = self.calc_bonus(new_node.observation)
                
                new_node.score = score + bonus
                new_node.goal = self.model.GOAL_TEST(new_node.observation)
                new_node.depth = depth + 1
                self.putdown_nodes.append(new_node)
    
    def custom_search(self, observation):
        self.num_piles = self.model.NUM_PILES(observation)
        
        actions = self.model.ACTIONS(observation)
        self.max_score = self.model.EVALUATE(observation)
        
        # Generate Pickup Nodes
        process_nodes = []
        for action in actions:
            if action == 0:
                continue
            if action > 0 and action <= self.num_piles:
                pickup_node = PickupNode()
                pickup_node.action = action
                pickup_node.observation = self.model.RESULT(observation, action)
                pickup_node.depth = 1
                process_nodes.append(pickup_node)
            if action > self.num_piles:
                continue
        
        # Process Pickup Nodes
        for node in process_nodes:
            self.HANDLE_PICKUP_NODE(node)
        
        # Filter all putdown nodes that have a score less than the max score
        # filtered_putdown_nodes = [node for node in self.putdown_nodes if node.score >= self.max_score]
        filtered_putdown_nodes = self.putdown_nodes
        
        if len(filtered_putdown_nodes) == 0:
            self.actions = [0]
            return
        
        # Select the best putdown node and generate the action sequence
        selected_node = self.select_best_putdown_node(filtered_putdown_nodes)
        computed_actions = self.generate_action_sequence(selected_node)
        
        # Cycle through actions until a new valid sequence is found
        while True:
            filtered_putdown_nodes.remove(selected_node)
            if len(filtered_putdown_nodes) == 0:
                computed_actions = [0]
                break
            if self.validate_actions(observation, computed_actions):
                break
            selected_node = self.select_best_putdown_node(filtered_putdown_nodes)
            computed_actions = self.generate_action_sequence(selected_node)
    
        self.actions = computed_actions
    
    def select_best_putdown_node(self, nodes):
        max_node = max(nodes)
        
        r_node = random.choice(nodes)
        while r_node.score < max_node.score:
            r_node = random.choice(nodes)
        max_node = r_node
        
        return max_node

    def generate_action_sequence(self, max_node):
        computed_actions = []
        while max_node is not None:
            computed_actions.append(max_node.action)
            max_node = max_node.parent_node
        return computed_actions
    
    def validate_actions(self, observation, computed_actions):
        reversed_computed_actions = computed_actions.copy()
        reversed_computed_actions.reverse()
        test_obs = observation
        actions_valid = True
        for action in reversed_computed_actions:
            if action == 0:
                continue
            avaliable_actions = self.model.ACTIONS(test_obs)
            if action not in avaliable_actions:
                actions_valid = False
                break
            test_obs = self.model.RESULT(test_obs, action)
        return actions_valid
    
    def calc_bad_search_limit(self, observation):
        
        bank_size = len(observation['bank'])
        num_piles = len(observation['piles'].values())
        
        if bank_size == 0:
            return 30
        
        num_faceup_cards = 0
        for pile in observation['piles'].values():
            for card in pile:
                if card[2] == 1:
                    num_faceup_cards += 1
        
        num_banks = bank_size // num_piles
        
        return self.bad_search_limit - num_banks
        

    # interesting seeds 26, 37, 46, 50, 51, 63, 88*, 98*, 5**,  

    def agent_function(self, observation):
        
        bad_search_limit = self.calc_bad_search_limit(observation)
        
        if len(self.actions) == 0:
            logging.info("--------------------------------    Evaluationg Search...  ---------------------------------")
            if self.bad_search_counter == 0:
                self.score_before_bad_search = self.model.EVALUATE(observation)
                self.bad_search_counter += 1
            else:
                if self.model.EVALUATE(observation) < self.score_before_bad_search:
                    self.bad_search_counter += 1
                else:
                    self.score_before_bad_search = self.model.EVALUATE(observation)
                    self.bad_search_counter = 0
            
            if self.bad_search_counter >= bad_search_limit:
                logging.info("Bad Search Detected")
                self.bad_search_counter = 0
                # print("Bad Search Detected")
                # input("Press Enter to Continue...")
                return 0
            
            logging.info("--------------------------------    Calculating Search...  ---------------------------------")
            self.custom_search(observation)
            
            if len(self.actions) != 0:
                logging.info(f"Actions: {self.actions}")
                logging.info("--------------------------------    Search Calculated  ---------------------------------")
            else:
                logging.info("No Actions Found")
                logging.info(f"Actions: {self.actions}")
                logging.info("--------------------------------    Search Failed  ---------------------------------")
                raise Exception("No Actions Found")
        
        action = self.actions.pop()
        
        # if action == 0:
        #     input("Press Enter to Continue...")
        
        return action