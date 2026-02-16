Spider Solitare
-------------
![Spider_Solitare](https://github.com/user-attachments/assets/edc468b7-96ce-494b-acb2-bde10089f83e)

Action Space
```python
Discrete(number_of_piles * 2 + 1) (default 10 piles)
```
Observation Space
```python
card_space = spaces.MultiDiscrete([number_of_ranks + 1, number_of_suits + 1, 2])

pile_space = spaces.Sequence(card_space, stack=True) completed_suit_space = spaces.Sequence(card_space, stack=True)

Dict({
  "bank": spaces.Sequence(card_space, stack=True),
  "completed_suits": spaces.Dict({
    f"completed_suit_{i+1}": completed_suit_space for i in range(num_completed_suits)
  }),
  "hand": spaces.Sequence(card_space),
  "piles": spaces.Dict({
    f"pile_{i+1}": pile_space for i in range(num_piles)
  }),
  "pickup_pile_index": spaces.Discrete(num_piles + 1),
  "num_moves": spaces.Discrete(600),
  "score": spaces.Discrete(2000, start=-999)
})
```
Import
```python
gymnasium.make("spider\_solitare/SpiderSolitare-v0")
```
### _Description_

The game starts with a standard spider solitaire setup. Two decks of 52 cards (13 ranks per suit) were shuffled, then divided into 10 piles with 50 cards dealt to the bank. The top card of each pile is turned face up while the remaining cards are face down.

The goal of the game is to sort out all the cards by their suit and rank. A winning game has each pile cleared of cards and 8 completed suits of 13 cards.


### _Observation Space_

Each card is represented by a three tuple. 

- Card\[0] represents the rank (from 1-13)

- Card\[1] represents the suit (from 0-4)

- Card\[2] represents a faceup/facedown state (0 for face down, 1 for face up)

A hidden card will have a 0 in each position.

The observation space is a dictionary containing the following sub-spaces:

- **Bank** - contains all cards that are not currently in the game.

- **Completed Suits** - contains all cards that are found to be in a completed suit.  A default game has 8 completed suit slots with a capacity of 13 cards each.

- **Hand** - This is a stack data structure of cards. Cards that are picked up are pushed to this stack. The hand space dumps all cards during a putdown action.

- **Piles** - A default game has 10 piles. Each pile is a stack data structure containing each card. Cards can be popped onto a pile from the hand or they can be popped off the pile to the hand. Each pile is listed by the “pile\_{index}” key where the index represents piles from 1 to 10. There is no pile 0.

- **Pickup Pile Index** - The index of the most recent pickup action. Since cards can only be picked up from one pile at a time, any pickup action will update this flag with the pile index selected. Put down actions update the Pickup Pile Index back to zero indicating to the agent that a card can again be picked up from any pile.

- **Num Moves** - The total number of moves taken by the agent. A move is defined by either a put-down action or a draw-bank action.

- **Score** - the current game score (Sun Microsystems 1989) minus the number of moves taken.


### _Action Space_

The normal rules of spider solitaire apply. You can only move cards that are face up from pile to pile. Cards can only be placed on each other if they are one rank less than the card below. If a face-up card is moved from a pile with face-down cards, the top face-down card is turned over.  The bank can deal one card on top of each pile, (this game allows for bank deals with empty piles)

The environment accepts actions as numbers between {0, 2 times the number of piles}.  

- Action 0 will always be the draw from bank action. Draw bank actions are only allowed if there are cards in the bank and if there are zero cards in the hand space.  

- Actions 1 through the number of piles are pickup actions. Any time a card is picked up, it is placed in the hand space in the order it was picked up. The pickup\_pile\_index is updated to the index of the pile most recently picked up from. The environment only allows additional pickup actions that are from the same pickup\_pile\_index, (aka: you can only pick up cards from one pile at a time).   

- Actions 1 + number of piles through 2 \*  the number of piles is designated as a put down action, where the action is the index (minus the number of piles) the cards in the hand will be put down. Put-down actions are only valid if there are cards in the hand space. A put-down action will clear all cards from the hand and update the pickup\_pile\_index to zero.


### _Starting State_

The game will begin with the cards already shuffled and dealt into the piles and bank.

- These piles are listed as “pile\_1” through “pile\_10” 

  - (with 10 being the default number of piles). 

  - Call cards in each pile will be hidden except the top card in each pile.

- The bank will have 50 cards in a standard game.

  - All 50 cards are also hidden.

- The remaining spaces, (i.e. the hand and completed\_suits) will have zero cards.

- The num\_moves, score, and pickup\_pile\_index are initialized to zero.


### _Reward_

Each time a card or group of cards are moved from one pile to another, or if a bank deal takes place, that counts as one move. Scores are calculated after each move following the scoring system from Sun Microsystems' implementation of Spider Solitaire in 1989 with the addition of move count penalties(see The performance Measure in the PEAS assessment). The highest possible score using the Sun Microsystems implementation is 1000 points. The space allows for a score of -999 to 1000 due to the potential for move penalties.

The environment will check each pile after each move for completed suits. A completed suit is one card of each rank of the same suit in order of rank from highest to lowest. Completed suits are moved to the completed suit space as they are found and additional score points are added.


### _Episode End_

The game/episode will terminate if the agent takes an invalid action.

The game/episode will truncate after 750 actions are taken by default.


### _Arguments_
```python
gym.make(   'spider_solitare/SpiderSolitare-v0',   render_mode,   num_suits,   max_episode_steps,   theme )
```
- render\_mode (None, ‘ansi’)

  - None - no render

  - ‘ansi’ - render the game in the terminal with ascii

- num_suits (1, 2, 4) - Number of suits per deck.

- max_episode_steps

  - Number of actions allowed before truncating the episode.

  - Default 750 steps.

- theme (‘light’, ‘dark’)

  - changes the color scheme in the ansi render for dark terminals or light terminals.  

  - default ‘dark’


### _References_

Wikimedia Foundation. (2024, August 15). Spider (solitaire). Wikipedia. <https://en.wikipedia.org/wiki/Spider_(solitaire)>


### _Version History_

- v0: Initial version release
