Spider Solitare Environment
-------------------------

# Description

The state is a standard setup for a spider solitare game.
The goal is to sort each suite of cards from ace to king.

# Observation Space

An observation returns a dictionary with the following information:

- "bank": The cards avalible in the bank.
- "completed_suits": this is the cards in each completed suit, A completed suit has either 0 (empty) or 13 (completed) cards.
- "hand": the cards in the agents hand.
- "piles": the cards in each pile.
- "pickup_pile_index": This is the index of the pile from the most recently picked up card.  If there are no cards picked up, this index is 0.
- "num_moves": Total number of moves taken.
- "score": current score of the game.

## Card Space
A card is represented by a len 3 numpy array.
- index 0: the rank of the card
- index 1: the suit of the card
- index 2: 1 = the card is face up, 0 = the card is face down.
Face down cards will have a rank and suit of 0.

# Action Space

Action space is represented by a number between 0 and the number of piles (default 10) multiplied by 2 (20) inclusive.

- Action 0 is always the draw from bank action.  This places one card on each pile from the bank.
- Actions 1 through number of piles are pickup actions where the number represents the index of the pile to pickup the card from.
- Actions num_piles+1 through num_piles*2 are putdown actions.  This follows the same index system as the pickup actions.

# Starting State

The starting state represents two decks, four suits per deck, of shuffled cards dealed in the standard spider solitare layout.
- Ten (default) piles delt left to right untill only 50 cards remain in the bank.
- the first card of each pile is turned face up while the remaining cards are left face down.

# Rewards

The score/reward is recalculated from zero each step of the game using the following scoreing system.

- 10 * (number of face-down cards turned face up): For each initial face-down card that
gets turned over, the agent is awarded 10 points.
- 15 * (number of piles that contain zero face-down cards):
- 2 * (number of cards placed atop the next higher card of the same suit)
- 50 * (number of completed suits)
- 2 * (number of completed suits after the first three): If the game ends with 4 or more
completed suits still in the tableau, add 2 points for each suit after the first three.
- -1 * (number of moves taken): this is a penalty.

# Episode End

The episode terminates when all of the cards are in their completed suits.

The episode will truncate after 600 steps. This limit can
be overridden with the `max_episode_steps` parameter to 
`gymnasium.make()`.

