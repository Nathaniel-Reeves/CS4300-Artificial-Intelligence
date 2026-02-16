import numpy as np
import copy
import random
import logging
from enum import Enum

class MarbleSolitareBoardTypes(Enum):
    ENGLISH = 'english'
    EUROPEAN = 'european'
    EUROPEAN_CORNER = 'european_corner'  # European board with empty spot at inner corner (1,1)
    EUROPEAN_FRENCH = 'european_french'  # European board with empty spot one above center (2,3)
    # TRIANGULAR = 'triangular' implement later

'''Represents the state of the marble solitare board

    . = empty
    O = marble
    
    European Board layout:
        . . .
      . . . . .
    . . . . . . . 
    . . . . . . .
    . . . . . . .
      . . . . .
        . . .
        
    English Board layout:
        . . .
        . . .
    . . . . . . .
    . . . . . . .
    . . . . . . .
        . . .
        . . .
    
    index mapping (European board):
     00     01    (02)   (03)   (04)    05     06
     07    (08)   (09)   (10)   (11)   (12)    13
    (14)   (15)   (16)   (17)   (18)   (19)   (20)
    (21)   (22)   (23)   (24)   (25)   (26)   (27)
    (28)   (29)   (30)   (31)   (32)   (33)   (34)
     35    (36)   (37)   (38)   (39)   (40)    41
     42     43    (44)   (45)   (46)    47     48
    
    where () indicates a valid position on the board
    
    Positions 8, 12, 36, 40 can be set as invalid positions
    for the English type of marble solitare board.
    
    The state is represented as a list of integers, where:
    0 = empty
    1 = marble
    -1 = invalid position
    
    the max x and max y represent the dimensions of the board,
    which are 7 and 7 respectively by default,
    but can be changed for different board configurations.
    
    The state also keeps track of the number of marbles left on the board,
    and the number of moves made so far.
    
    '''

class MarbleSolitareState:
    
    def __init__(self, max_x=7, max_y=7, board_type=MarbleSolitareBoardTypes.EUROPEAN_FRENCH):
        """Initialize a marble solitaire state.
        
        Args:
            max_x: Width of the board (default 7)
            max_y: Height of the board (default 7)
            board_type: MarbleSolitareBoardTypes enum value
        """
        self._max_x = max_x
        self._max_y = max_y
        self._board_type = board_type if isinstance(board_type, MarbleSolitareBoardTypes) else MarbleSolitareBoardTypes(board_type)
        self._board = None
        self._marbles_left = 0
        self._moves_made = 0
    
    def create_board(self):
        """Create the initial marble solitaire board.
        
        For a 7x7 board:
        - English: corners at (0,0), (0,1), (1,0), (1,1), (0,5), (0,6), (1,5), (1,6),
                   (5,0), (5,1), (6,0), (6,1), (5,5), (5,6), (6,5), (6,6) are invalid
        - European: diagonal corners are invalid
        - European Corner: Same as European but empty spot at (1,1) instead of center
        - European French: Same as European but empty spot at (2,3) - one above center
        
        Center position starts empty, all valid positions have marbles.
        """
        # Initialize board with all marbles
        self._board = np.ones((self._max_y, self._max_x), dtype=int)
        
        if self._board_type == MarbleSolitareBoardTypes.ENGLISH:
            self._create_english_board()
        elif self._board_type == MarbleSolitareBoardTypes.EUROPEAN:
            self._create_european_board()
        elif self._board_type == MarbleSolitareBoardTypes.EUROPEAN_CORNER:
            self._create_european_board()  # Same layout as European
        elif self._board_type == MarbleSolitareBoardTypes.EUROPEAN_FRENCH:
            self._create_european_board()  # Same layout as European
        
        # Set empty position based on board type
        if self._board_type == MarbleSolitareBoardTypes.EUROPEAN_CORNER:
            # Empty spot at inner corner (1, 1) - index 8 in the comment above
            self._board[1, 1] = 0
        elif self._board_type == MarbleSolitareBoardTypes.EUROPEAN_FRENCH:
            # Empty spot one above center (2, 3) - French style
            self._board[2, 3] = 0
        else:
            # Center position starts empty (3, 3 for a 7x7 board)
            center_y = self._max_y // 2
            center_x = self._max_x // 2
            self._board[center_y, center_x] = 0
        
        # Count marbles
        self._marbles_left = np.sum(self._board == 1)
        self._moves_made = 0
    
    def _create_english_board(self):
        """Mark invalid positions for English board layout."""
        # Top-left corner
        self._board[0, 0] = -1
        self._board[0, 1] = -1
        self._board[1, 0] = -1
        self._board[1, 1] = -1
        # Top-right corner
        self._board[0, 5] = -1
        self._board[0, 6] = -1
        self._board[1, 5] = -1
        self._board[1, 6] = -1
        # Bottom-left corner
        self._board[5, 0] = -1
        self._board[5, 1] = -1
        self._board[6, 0] = -1
        self._board[6, 1] = -1
        # Bottom-right corner
        self._board[5, 5] = -1
        self._board[5, 6] = -1
        self._board[6, 5] = -1
        self._board[6, 6] = -1
    
    def _create_european_board(self):
        """Mark invalid positions for European board layout.
        
        European board has a more rounded/diamond shape compared to English.
        Only the corner-most positions are invalid.
        Position (1,1) and its symmetric positions are valid for the European variant.
        """
        # Top-left corner (only the 2 most extreme positions)
        self._board[0, 0] = -1
        self._board[0, 1] = -1
        self._board[1, 0] = -1
        
        # Top-right corner
        self._board[0, 5] = -1
        self._board[0, 6] = -1
        self._board[1, 6] = -1
        
        # Bottom-left corner
        self._board[5, 0] = -1
        self._board[6, 0] = -1
        self._board[6, 1] = -1
        
        # Bottom-right corner
        self._board[5, 6] = -1
        self._board[6, 5] = -1
        self._board[6, 6] = -1
    
    @property
    def observation(self):
        """Return the current observation dict."""
        return {
            'board': self._board.copy() if self._board is not None else None,
            'marbles_left': np.array(self._marbles_left, dtype=np.int64),
            'moves_made': np.array(self._moves_made, dtype=np.int64)
        }
    
    @observation.setter
    def observation(self, value):
        """Set the state from an observation dict."""
        if value is not None:
            self._board = value['board'].copy() if value['board'] is not None else None
            self._marbles_left = int(value['marbles_left'])
            self._moves_made = int(value['moves_made'])
    
    def __repr__(self):
        """String representation of the board."""
        if self._board is None:
            return "MarbleSolitareState(uninitialized)"
        
        output = f"MarbleSolitareState({self._board_type}, marbles={self._marbles_left}, moves={self._moves_made})\\n"
        for row in self._board:
            row_str = ""
            for cell in row:
                if cell == -1:
                    row_str += "  "
                elif cell == 0:
                    row_str += ". "
                elif cell == 1:
                    row_str += "O "
            output += row_str + "\\n"
        return output

class MarbleSolitareModel:
    
    def __init__(self):
        return
    
    def ACTIONS(self, observation):
        """Return list of valid actions (moves) from current state.
        
        An action is a tuple: (from_y, from_x, to_y, to_x)
        Valid move: jump a marble over an adjacent marble into an empty space.
        
        Args:
            observation: Dict with 'board', 'marbles_left', 'moves_made'
            
        Returns:
            List of valid action tuples
        """
        logging.debug("===================== CALLING ACTIONS =====================")
        
        board = observation['board']
        actions = []
        
        # Check all positions
        for y in range(board.shape[0]):
            for x in range(board.shape[1]):
                # Only check positions with marbles
                if board[y, x] != 1:
                    continue
                
                # Check all 4 directions: up, down, left, right
                directions = [
                    (-1, 0),  # up
                    (1, 0),   # down
                    (0, -1),  # left
                    (0, 1)    # right
                ]
                
                for dy, dx in directions:
                    # Position of marble to jump over
                    jump_y = y + dy
                    jump_x = x + dx
                    # Landing position
                    land_y = y + 2 * dy
                    land_x = x + 2 * dx
                    
                    # Check bounds
                    if (0 <= jump_y < board.shape[0] and 
                        0 <= jump_x < board.shape[1] and
                        0 <= land_y < board.shape[0] and 
                        0 <= land_x < board.shape[1]):
                        
                        # Valid move if: jumping over a marble into an empty space
                        if board[jump_y, jump_x] == 1 and board[land_y, land_x] == 0:
                            actions.append((y, x, land_y, land_x))
        
        logging.debug(f"Actions: {actions}")
        logging.debug("===================== END ACTIONS =====================")
        return actions
    
    def RESULT(self, observation, action):
        """Apply an action to the observation and return the new observation.
        
        Args:
            observation: Dict with 'board', 'marbles_left', 'moves_made'
            action: Tuple (from_y, from_x, to_y, to_x)
            
        Returns:
            New observation dict after applying the action
        """
        logging.debug("===================== CALLING RESULT =====================")
        
        # Create state from observation
        state = MarbleSolitareState()
        state.observation = observation
        
        # Make a deep copy to avoid modifying original
        state_copy = copy.deepcopy(state)
        
        # Extract action coordinates
        from_y, from_x, to_y, to_x = action
        
        # Calculate jumped marble position
        jump_y = (from_y + to_y) // 2
        jump_x = (from_x + to_x) // 2
        
        # Apply the move to the copied board
        board = state_copy._board
        board[from_y, from_x] = 0  # Remove marble from source
        board[jump_y, jump_x] = 0  # Remove jumped marble
        board[to_y, to_x] = 1      # Place marble at destination
        
        # Update marble count and moves
        state_copy._marbles_left = np.sum(board == 1)
        state_copy._moves_made += 1
        
        # Get the updated observation
        obs = state_copy.observation
        
        logging.debug(f"Action: {action}")
        logging.debug(f"Observation: {obs}")
        logging.debug("===================== END RESULT =====================")
        return obs
        
    def GOAL_TEST(self, observation):
        """Check if the goal state has been reached.
        
        Goal: Only 1 marble remaining on the board.
        
        Args:
            observation: Dict with 'board', 'marbles_left', 'moves_made'
            
        Returns:
            True if goal is reached, False otherwise
        """
        logging.debug("===================== CALLING GOAL_TEST =====================")
        
        marbles_left = observation['marbles_left']
        goal = marbles_left == 1
        
        logging.debug(f"Marbles left: {marbles_left}")
        logging.debug(f"Goal: {goal}")
        logging.debug("===================== END GOAL_TEST =====================")
        return goal
    
    def STEP_COST(self, observation, action):
        """Return the cost of taking an action.
        
        In marble solitaire, each move has a uniform cost of -1 (negative reward).
        This encourages the agent to reach the goal in fewer moves.
        
        Args:
            observation: Dict with 'board', 'marbles_left', 'moves_made'
            action: Tuple (from_y, from_x, to_y, to_x)
            
        Returns:
            Cost/reward for the action
        """
        logging.debug("===================== CALLING STEP_COST =====================")
        
        # Standard cost per move is -1 (penalize each move)
        cost = -1
        
        logging.debug(f"Cost: {cost}")
        logging.debug("===================== END STEP_COST =====================")
        return cost
    
    def EVALUATE(self, observation):
        """Evaluate the quality of a state.
        
        Lower number of marbles is better. Returns negative of marbles remaining.
        Goal state (1 marble) gets highest score of -1.
        
        Args:
            observation: Dict with 'board', 'marbles_left', 'moves_made'
            
        Returns:
            Evaluation score (higher is better)
        """
        logging.debug("===================== CALLING EVALUATE =====================")
        
        marbles_left = observation['marbles_left']
        
        # Negative marbles remaining (fewer marbles = higher score)
        value = -marbles_left
        
        logging.debug(f"Marbles left: {marbles_left}")
        logging.debug(f"Value: {value}")
        logging.debug("===================== END EVALUATE =====================")
        return value
    
    def HEURISTIC(self, observation):
        """Heuristic function to estimate cost to reach goal.
        
        Estimates remaining moves needed. Since each move removes one marble,
        the heuristic is approximately (marbles_left - 1).
        
        Args:
            observation: Dict with 'board', 'marbles_left', 'moves_made'
            
        Returns:
            Estimated cost to reach goal
        """
        logging.debug("===================== CALLING HEURISTIC =====================")
        
        marbles_left = observation['marbles_left']
        
        # Estimate: each move removes 1 marble, need to get from N marbles to 1
        # So approximately (marbles_left - 1) moves remaining
        heuristic_value = marbles_left - 1
        
        logging.debug(f"Marbles left: {marbles_left}")
        logging.debug(f"Heuristic Value: {heuristic_value}")
        logging.debug("===================== END HEURISTIC =====================")
        return heuristic_value

if __name__ == "__main__":
    s = MarbleSolitareState()
    print(s)