import numpy as np
import copy
import random
import logging

class SpiderSolitareState:

    def __init__(self, num_suits=4):
        
        # Validate num_suits to 4, 2, or 1
        if num_suits not in [4, 2, 1]:
            raise ValueError("num_suits must be 4, 2, or 1.")
        
        self._num_decks = 2
        self._num_suits = num_suits
        self._num_ranks = 13
        self._num_piles = 10
        self._num_completed_suits = 8
        self._piles = {f"pile_{i+1}": tuple() for i in range(self._num_piles)}
        self._completed_suits = {f"completed_suit_{i+1}": tuple() for i in range(self._num_completed_suits)}
        self._bank = tuple()
        self._hand = tuple()
        self._pickup_pile_index = 0
        self._num_moves = 0
        self._score = 0
        
        return None
    
    @property
    def num_piles(self):
        return self._num_piles
    
    @property
    def pickup_pile_index(self):
        return self._pickup_pile_index
    
    @property
    def hand(self):
        return self._hand
    
    @property
    def num_suits(self):
        return self._num_suits
    
    @property
    def completed_suits(self):
        return self._completed_suits
    
    @property
    def piles(self):
        return self._piles

    @pickup_pile_index.setter
    def pickup_pile_index(self, value):
        self._pickup_pile_index = value
        return
    
    def create_deck(self):
        deck = []
        for _ in range(self._num_decks):
            for rank in range(1, self._num_ranks + 1):
                for i in range(1, 5):
                    suit = i
                    if self._num_suits == 1:
                        suit = 1
                    if self._num_suits == 2:
                        suit = i % 2 + 1
                    card = np.array([rank, suit, 0])
                    deck.append(card)
        return deck

    def deal(self, seed=None):
        deck = self.create_deck()
        if seed is not None:
            print("SEED: ", seed)
            random.seed(seed)
            np.random.seed(seed)
        random.shuffle(deck)
        
        # Deal 54 cards to the piles
        piles = [[] for _ in range(10)]
        for i in range(54):
            piles[i % 10].append(deck.pop())
        
        # Turn over top card in each pile
        for pile in piles:
            last_card = pile[-1]
            last_card[2] = 1
        
        # Move temp piles to state
        self._piles = {f"pile_{i+1}": tuple(pile) for i, pile in enumerate(piles)}
        
        # Deal remaining cards to bank
        self._bank = tuple(deck)
        
        return self.return_state()

    def return_state(self):
        # print("RETURNING STATE")
        self.calculate_score()
        return {
            "bank": self._bank,
            "completed_suits": self._completed_suits,
            "hand": self._hand,
            "piles": self._piles,
            "pickup_pile_index": self._pickup_pile_index,
            "num_moves": self._num_moves,
            "score": self._score
        }

    def deal_from_bank(self):
        # for pile in self._piles.values():
        #     if len(pile) == 0:
        #         logging.warning("Deal Failed: All piles must have at least one card.")
        #         return self.return_state()
            
        if len(self._bank) == 0:
            logging.warning("Deal Failed: Bank must have at least one card.")
            return self.return_state()
        
        if len(self._hand) > 0:
            logging.warning("Deal Failed: Hand must be empty.")
            return self.return_state()
        
        for key in self._piles.keys():
            pile = list(self._piles[key])
            self._bank = list(self._bank)
            
            card = self._bank.pop()
            card[2] = 1
            pile.append(card)
            
            pile = tuple(pile)
            self._bank = tuple(self._bank)
            self._piles[key] = pile
            self._num_moves += 1
        self._update_state()
        return self.return_state()

    def pickup_card(self, pile_index):
        
        # Pile index must be between 1 and num piles
        if pile_index < 1 or pile_index > self._num_piles:
            logging.warning("Pickup Failed: Pile index must be between 1 and 10.")
            return self.return_state()
        
        pile = copy.deepcopy(self._piles[f"pile_{pile_index}"])
        pile = list(pile)
        
        # Pile must have at least one card
        if len(pile) == 0:
            logging.warning("Pickup Failed: Pile must have at least one card.")
            return self.return_state()
        
        if len(self._hand) == 0:
            card = pile.pop()
            self._piles[f"pile_{pile_index}"] = tuple(pile)
            hand = [card]
            self._hand = tuple(hand)
            
        else:
            if len(self._hand) > 0 and self._pickup_pile_index == 0:
                logging.warning("Pickup Failed: Hand is not empty but pickup pile index is 0.")
                return self.return_state()
            
            # You can only pickup a card from the same pile
            if (self._pickup_pile_index != pile_index):
                logging.warning("Pickup Failed: You can only pickup a card from the same pile.")
                return self.return_state()
            
            hand = list(self._hand)
            last_card_from_hand = hand[-1]
            pickup_card = pile.pop()
            
            # If the card you pickup is face down, you can't pickup it up
            if pickup_card[2] == 0:
                logging.warning("Pickup Failed: If the card you pickup is face down, you can't pickup it up.")
                return self.return_state()
            
            # The card you pickup must be one less rank than the last card in your hand
            # and it must be the same suit as the other cards in your hand
            if last_card_from_hand[0] + 1 != pickup_card[0] or last_card_from_hand[1] != pickup_card[1]:
                print("LAST CARD FROM HAND:", last_card_from_hand)
                print("PICKUP CARD:", pickup_card)
                logging.warning("Pickup Failed: The card you pickup must be one less rank than the last card in your hand and it must be the same suit as the other cards in your hand.")
                return self.return_state()
            
            hand.append(pickup_card)
            self._hand = tuple(hand)
            self._piles[f"pile_{pile_index}"] = tuple(pile)
        
        self._pickup_pile_index = pile_index
        return self.return_state()
    
    def put_down_cards(self, put_down_pile_index):
        if len(self._hand) == 0:
            logging.warning("Put Down Failed: Hand must have at least one card.")
            return self.return_state()
        
        if put_down_pile_index == 0:
            logging.warning("Put Down Failed: Put down pile index must be between 1 and 10.")
            return self.return_state()
        
        hand = list(self._hand)
        last_card_from_hand = hand[-1]
        pile = list(self._piles[f"pile_{put_down_pile_index}"])
        if len(pile) > 0:
            top_card_on_pile = pile[-1]
        else:
            top_card_on_pile = [0, 0, 0]
        
        if self.pickup_pile_index != put_down_pile_index and last_card_from_hand[0] != top_card_on_pile[0] - 1 and len(pile) != 0:
            print("PICKUP PILE INDEX:", self.pickup_pile_index)
            print("PUT DOWN PILE INDEX:", put_down_pile_index)
            print("LAST CARD FROM HAND:", last_card_from_hand)
            print("TOP CARD ON PILE:", top_card_on_pile)
            logging.warning("Put Down Failed: The card you put down must be one less rank than the top card on the pile or the pile must be empty.")
            return self.return_state()
        
        hand.reverse()
        pile.extend(hand)
        self._piles[f"pile_{put_down_pile_index}"] = tuple(pile)
        self._hand = tuple()
        self._pickup_pile_index = 0
        self._num_moves += 1
        self._update_state()
        return self.return_state()
    
    def _update_state(self):
        piles = copy.deepcopy(self._piles)
        
        
        for key in piles.keys():
            pile = list(piles[key])
            
            # Check if the pile contains a complete set of cards of the same suit from ace to king
            if len(pile) >= 13 and pile[-1][0] == 1:
                top_card = pile[-1]
                completed_suit = True
                for i in range(1, 13):
                    card = pile[-1-i]
                    if card[0] != top_card[0] + i or card[1] != top_card[1]:
                        completed_suit = False
                        break

                if completed_suit:
                    # If the loop completes without breaking, the pile contains a complete set of cards
                    # of the same suit from ace to king
                    completed_suit = []
                    for _ in range(13):
                        card = pile.pop()
                        completed_suit.append(card)
                    completed_suit.reverse()
                    
                    index = None
                    for ckey in self._completed_suits.keys():
                        if len(self._completed_suits[ckey]) == 0:
                            index = ckey
                            break
                    self._completed_suits[index] = tuple(completed_suit)
                    piles[key] = tuple()
            
            # Unhide the first card in the pile
            for i in range(len(pile)-1, -1, -1):
                # If the first card is hidden and there are no cards on top of it
                # and there are no cards in the hand, unhide the first card
                if i == len(pile)-1 and pile[i][2] == 0 and len(self._hand) == 0:
                    pile[i][2] = 1
            
            piles[key] = tuple(pile)
        self._piles = piles
        return self.return_state()
    
    def calculate_score(self):
        score = 44 * 10 # 44 face down cards initially
        
        # face down card turned up (10*n)
        for pile in self._piles.values():
            for card in pile:
                if card[2] == 0:
                    score -= 10
                    logging.debug(f"FACE DOWN CARD TURNED UP: {score}")
        
        # piles that contain zero face down cards (15*n)
        for pile in self._piles.values():
            zero_face_down_cards = True
            for card in pile:
                if card[2] == 1:
                    zero_face_down_cards = False
                    break
            if zero_face_down_cards:
                score += 15
                logging.debug(f"PILES THAT CONTAIN ZERO FACE DOWN CARDS: {score}")
        
        # cards placed ontop the next rank of the same suit (2*n)
        for pile in self._piles.values():
            for i in range(len(pile)-1):
                if pile[i][0] + 1 == pile[i+1][0] and pile[i][1] == pile[i+1][1] and pile[i][2] == 1 and pile[i+1][2] == 1:
                    score += 2
                    logging.debug(f"CARDS PLACED ONTOP THE NEXT RANK OF THE SAME SUIT: {score}")
        
        # number of completed suits (50*n)
        for key in self._completed_suits.keys():
            if len(self._completed_suits[key]) == 13:
                score += 50
                logging.debug(f"NUMBER OF COMPLETED SUITS: {score}")
        
        # number of completed suits after the first three (n*2)
        completed_suits = 0
        for key in list(self._completed_suits.keys())[3:]:
            if len(self._completed_suits[key]) == 13:
                completed_suits += 1
        if completed_suits > 3:
            score += completed_suits * 2
            logging.debug(f"NUMBER OF COMPLETED SUITS AFTER THE FIRST THREE: {score}")
        
        # number of moves taken (-1*n)
        score -= self._num_moves
        logging.debug(f"NUMBER OF MOVES TAKEN: {score}")
        
        self._score = score
        return score
    
    @property
    def observation(self):
        return self.return_state()

    @observation.setter
    def observation(self, value):
        self._piles = value["piles"]
        self._completed_suits = value["completed_suits"]
        self._bank = value["bank"]
        self._hand = value["hand"]
        self._pickup_pile_index = value["pickup_pile_index"]
        self._num_moves = value["num_moves"]
        self._score = value["score"]
        return
    
    def __repr__(self):
        return f"SpiderSolitareState(num_suits={self._num_suits}, piles={self._piles}, completed_suits={self._completed_suits}, bank={self._bank}, hand={self._hand})"

if __name__ == "__main__":
    s = SpiderSolitareState()
    print(s)

class SpiderSolitareModel:
    
    def __init__(self):
        return

    def ACTIONS(self, observation):
        logging.debug("===================== CALLING ACTIONS =====================")
        state = SpiderSolitareState()
        state.observation = observation
        
        num_piles = state.num_piles
        pickup_piles_index = state.pickup_pile_index
        piles = state.piles
        hand = state.hand
        
        if len(hand) > 0 and pickup_piles_index == 0:
            print("HAND:", hand)
            print("PICKUP PILE INDEX:", pickup_piles_index)
            raise ValueError("Hand is not empty but pickup pile index is 0.")
        
        # no_empty_piles = True
        # for key in piles.keys():
        #     if len(piles[key]) == 0:
        #         no_empty_piles = False
        #         break

        bank_empty = len(state.observation["bank"]) == 0
        bottom_hand_card = hand[-1] if len(hand) > 0 else None
        
        next_pickup_index_card = None
        if pickup_piles_index > 0 and pickup_piles_index <= len(piles):
            if len(piles[f'pile_{pickup_piles_index}']) > 0:
                next_pickup_index_card = piles[f'pile_{pickup_piles_index}'][-1]
            
        # Handle draw from bank action
        # if the hand is empty and
        # there are no empty piles
        # then the draw from bank action is valid
        
        # draw_bank = len(hand) == 0 and no_empty_piles and not bank_empty
        draw_bank = len(hand) == 0 and not bank_empty
        
        # Handle pickup from pile actions
        pickup_mask = [False for _ in range(num_piles)]
        # if the hand is empty and,
        # the pile is not empty,
        # then the pickup aciton is valid
        if len(hand) == 0:
            for i in range(1, num_piles+1):
                if len(piles[f'pile_{i}']) > 0:
                    pickup_mask[i-1] = True
        else:
            # if the hand is not empty and,
            # the next pickup index card is one less rank than the bottom hand card and,
            # the next pickup index card is the same suit as the bottom hand card
            # the next pickup index card is face up
            # then the pickup action is valid
            if bottom_hand_card is not None and \
               next_pickup_index_card is not None and \
               next_pickup_index_card[0] == bottom_hand_card[0] + 1 and \
               next_pickup_index_card[1] == bottom_hand_card[1] and \
               next_pickup_index_card[2] == 1:

               pickup_mask[pickup_piles_index-1] = True
        
        # Handle put down pile actions
        put_down_mask = [False for _ in range(num_piles)]
        # if the hand is not empty and,
        # the bottom hand card is one less rank than the top card on the pile or,
        # the pile is empty
        # then the put down action is valid
        if len(hand) > 0:
            for i in range(1, num_piles+1):
                pile = piles[f'pile_{i}']
                if len(pile) == 0:
                    put_down_mask[i-1] = True
                else:
                    top_card_on_pile = pile[-1]
                    if bottom_hand_card is not None and \
                        bottom_hand_card[0] + 1 == top_card_on_pile[0] and \
                        top_card_on_pile[2] == 1:
                        put_down_mask[i-1] = True
                if i == pickup_piles_index:
                    put_down_mask[pickup_piles_index-1] = False
                    # then the put down action is valid on that pile
                    # if i == pickup_piles_index:
                    #     put_down_mask[pickup_piles_index-1] = True
        
        actions_mask = [draw_bank] + pickup_mask + put_down_mask
        actions = []
        
        for i, action in enumerate(actions_mask):
            if action:
                actions.append(i)
        
        logging.debug(f"Actions: {actions}")
        logging.debug("===================== END ACTIONS =====================")
        return actions

    def RESULT(self, observation, action):
        logging.debug("===================== CALLING RESULT =====================")
        logging.debug(f"Action: {action}")
        
        state = SpiderSolitareState()
        state.observation = observation
        state1 = copy.deepcopy(state)
        
        if action == 0:
            state1.deal_from_bank()
        
        if action > 0 and action <= state.num_piles:
            state1.pickup_card(action)
        
        if action > state.num_piles:
            state1.put_down_cards(action - state.num_piles)
        
        obs = state1.observation
        logging.debug("===================== END RESULT =====================")
        return obs

    def GOAL_TEST(self, observation):
        logging.debug("===================== CALLING GOAL TEST =====================")
        state = SpiderSolitareState()
        state.observation = observation
        completed_suits = state.completed_suits
        goal = all([len(completed_suits[key]) == 13 for key in completed_suits.keys()])
        logging.debug(f"Goal: {goal}")
        logging.debug("===================== END GOAL TEST =====================")
        return goal

    def STEP_COST(self, observation, action, new_observation):
        logging.debug("===================== CALLING STEP COST =====================")
        state = SpiderSolitareState()
        state.observation = new_observation
        
        score = state.calculate_score()
        
        logging.debug(f"Action: {action}")
        logging.debug(f"Step Cost: {score}")
        logging.debug("===================== END STEP COST =====================")
        return score
    
    def EVALUATE(self, observation):
        logging.debug("===================== CALLING EVALUATE =====================")
        state = SpiderSolitareState()
        state.observation = observation
        score = state.calculate_score()
        logging.debug(f"Score: {score}")
        logging.debug("===================== END EVALUATE =====================")
        return score
    
    def HEURISTIC(self, observation):
        logging.debug("===================== CALLING HEURISTIC =====================")
        state = SpiderSolitareState()
        state.observation = observation
        score = state.calculate_score()
        logging.debug(f"Score: {score}")
        logging.debug("===================== END HEURISTIC =====================")
        # return score
        return 0
    
    def IS_CHANCE_NODE(self, observation, action, next_observation):
        logging.debug("===================== CALLING IS CHANCE NODE =====================")
        state = SpiderSolitareState()
        state.observation = observation
        chance = False
        
        # If the action is 0, it is a chance node (bank draw)
        if action == 0:
            chance = True
        
        # If the action would flip over a face down card, it is a chance node
        first_obs_score = 44 * 10 # 44 face down cards initially
        
        # face down card turned up (10*n)
        for pile in state.piles.values():
            for card in pile:
                if card[2] == 0:
                    first_obs_score -= 10
        
        next_obs_score = 44 * 10 # 44 face down cards initially
        
        # face down card turned up (10*n)
        for pile in state.piles.values():
            for card in pile:
                if card[2] == 0:
                    next_obs_score -= 10
        
        if next_obs_score < first_obs_score:
            chance = True
        
        logging.debug(f"Chance: {chance}")
        logging.debug("===================== END IS CHANCE NODE =====================")
        return chance
    
    def NUM_PILES(self, observation):
        state = SpiderSolitareState()
        state.observation = observation
        return state.num_piles

if __name__ == "__main__":
    state = SpiderSolitareState()
    state.deal()
    observation = state.observation
    actions = SpiderSolitareModel.ACTIONS(observation)
    print(actions)
