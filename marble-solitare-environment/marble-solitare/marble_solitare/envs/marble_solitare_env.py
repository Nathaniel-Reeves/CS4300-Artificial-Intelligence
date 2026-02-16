import gymnasium
from gymnasium import spaces
from marble_solitare.envs.marble_solitare_model import MarbleSolitareModel
from marble_solitare.envs.marble_solitare_model import MarbleSolitareState
from marble_solitare.envs.marble_solitare_model import MarbleSolitareBoardTypes
import os
import logging
from enum import Enum

# Removed duplicate MarbleSolitareBoardTypes - imported from model
    
class RenderModes(Enum):
    # HUMAN = 'human'
    # RGB_ARRAY = 'rgb_array'
    TERMINAL = 'terminal'

class Themes(Enum):
    DARK = 'dark'
    LIGHT = 'light'

class MarbleSlotStates(Enum):
    EMPTY = 0
    MARBLE = 1
    INVALID = -1
    
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

class MarbleSolitareEnv(gymnasium.Env):
    
    metadata = {'render_modes': ['terminal']}
    
    def __init__(
        self,
        render_mode: RenderModes = RenderModes.TERMINAL,
        max_x: int = 7,
        max_y: int = 7,
        theme: Themes = Themes.DARK,
        type: MarbleSolitareBoardTypes = MarbleSolitareBoardTypes.EUROPEAN_FRENCH
    ):
        
        self._state = MarbleSolitareState()
        self._max_x = max_x
        self._max_y = max_y
        self._type = type
        self._theme = theme
        # Handle string or enum render_mode
        if render_mode == 'terminal' or render_mode == RenderModes.TERMINAL:
            self.render_mode = 'terminal'
        else:
            self.render_mode = None
        
        board_space = spaces.Box(low=-1, high=1, shape=(self._max_x, self._max_y), dtype=int)
        
        self.observation_space = spaces.Dict({
            'board': board_space,
            'marbles_left': spaces.Box(low=0, high=36, shape=(), dtype=int), # max 36 marbles for European board
            'moves_made': spaces.Box(low=0, high=100, shape=(), dtype=int) # arbitrary large number for moves made
        })
        
        self.action_space = spaces.MultiDiscrete([self._max_x, self._max_y, self._max_x, self._max_y]) # from_x, from_y, to_x, to_y
        
        return
    
    def reset(self, seed=None, options=None):
        self._state = MarbleSolitareState(self._max_x, self._max_y, self._type)
        self._state.create_board()
        self.render()
        return self._state.observation, {}
    
    def step(self, action):
        state = self._state
        model = MarbleSolitareModel()
        obs = state.observation
        
        valid_actions = model.ACTIONS(obs)
        if action not in valid_actions:
            if action != 0 and action is not None:
                print(f"Invalid action: {action}, valid actions are: {valid_actions}")
            score = model.STEP_COST(state.observation, action)
            terminated = True
            info = {"reason": "invalid action"}
            return state.observation, score, terminated, False, info
        
        new_obs = model.RESULT(obs, action)
        state1 = MarbleSolitareState(self._max_x, self._max_y, self._type)
        state1.observation = new_obs
        self._state = state1
        
        observation = self._state.observation
        reward = model.STEP_COST(obs, action)
        terminated = model.GOAL_TEST(observation) or not model.ACTIONS(observation)
        info = {}
        
        self.render()
        return observation, reward, terminated, False, info
    
    def render(self):
        if self.render_mode == 'terminal':
            print(self._render_text())
        return
    
    def _render_text(self):
        # clear screen, if logging level is set to warning
        if logging.getLogger().getEffectiveLevel() == logging.WARNING:
            os.system('cls' if os.name == 'nt' else 'clear')
        
        board = self._state.observation['board']
        marbles_left = self._state.observation['marbles_left']
        moves_made = self._state.observation['moves_made']
        
        info_frame = self._build_info_frame()
        info_frame = self._render_title(info_frame, mode=self._theme)
        info_frame = self._render_marbles_left(info_frame, marbles_left, mode=self._theme)
        info_frame = self._render_num_moves(info_frame, moves_made, mode=self._theme)
        info_frame = self._render_epilouge(info_frame, mode=self._theme)
        
        # Build board frame
        board_frame = self._render_board(board)
        
        # Combine frames side by side
        max_lines = max(len(board_frame), len(info_frame['frame']))
        combined = []
        
        # Add some blank lines at the top for better vertical centering
        for _ in range(2):
            combined.append("")
        
        for i in range(max_lines):
            line = ""
            if i < len(board_frame):
                line += board_frame[i]
            else:
                line += " " * (self._max_x * 2)  # Match board width
            
            # Add spacing between board and info
            line += "    "
            
            if i < len(info_frame['frame']):
                line += "".join(info_frame['frame'][i])
            
            combined.append(line)
        
        left_padding = 5
        lp = " " * left_padding
        
        out = ''
        for line in combined:
            out += f'{lp}{line}\n'
            
        return out
    
    def _render_board(self, board):
        """Render the board with 2x2 character representation for each slot.
        Each slot uses:
        - Top-left: state character (' ' for invalid, '.' for empty, 'O' for marble)
        - Top-right: space
        - Bottom-left: space
        - Bottom-right: space
        """
        lines = []
        for row in board:
            # Create two text lines for this board row (2x2 representation)
            top_line = ""
            bottom_line = ""
            
            for cell in row:
                if cell == MarbleSlotStates.INVALID.value:
                    top_line += "  "  # space + space
                elif cell == MarbleSlotStates.EMPTY.value:
                    top_line += ". "  # dot + space
                elif cell == MarbleSlotStates.MARBLE.value:
                    top_line += "O "  # O + space
                
                bottom_line += "  "  # space + space for bottom row
            
            lines.append(top_line)
            lines.append(bottom_line)
        
        return lines
    
    def _build_info_frame(self):
        height = 25
        
        frame = []
        for i in range(height):
            row = []
            frame.append(row)
        
        d = {
            'line': 0,
            'frame': frame,
        }
        
        return d
    
    def _render_title(self, info_frame, mode=Themes.DARK):
        
        c = style.WHITE
        if mode == Themes.LIGHT:
            c = style.BLACK

        left_padding = 6
        lp = " " * left_padding

        lines = []
        lines.append(list(f'{c}{lp}   __  ___           __   __        ____     ___ __              {style.RESET}'))
        lines.append(list(f'{c}{lp}  /  |/  /__ _____  / /  / /__     / __/__  / (_) /____ ________ {style.RESET}'))
        lines.append(list(f'{c}{lp} / /|_/ / _ `/ __/ / _ \\/ / -_)   _\\ \\/ _ \\/ / / __/ _ `/ __/ -_){style.RESET}'))
        lines.append(list(f'{c}{lp}/_/  /_/\\_,_/_/   /_.__/_/\\__/   /___/\\___/_/_/\\__/\_,_/_/  \\__/ {style.RESET}'))
        lines.append(list(f'{c}{lp}                                                                  {style.RESET}'))
        lines.append(list(f'{c}{lp}=========================================================================={style.RESET}'))
        
        starting_line = info_frame['line']
        for line in lines:
            info_frame['frame'][starting_line] = line
            starting_line += 1
        info_frame['line'] = starting_line
        
        return info_frame
    
    def _render_epilouge(self, info_frame, mode=Themes.DARK):
        
        c = style.WHITE
        if mode == Themes.LIGHT:
            c = style.BLACK

        left_padding = 6
        lp = " " * left_padding

        lines = []
        lines.append(list(f'{c}{lp}=========================================================================={style.RESET}'))
        lines.append(list(f'{c}{lp}     Created by: Nathaniel Reeves in February of 2026 as a side project{style.RESET}'))
        lines.append(list(f'{c}{lp}=========================================================================={style.RESET}'))
        
        starting_line = info_frame['line']
        for line in lines:
            info_frame['frame'][starting_line] = line
            starting_line += 1
        info_frame['line'] = starting_line
        
        return info_frame
    
    def _render_marbles_left(self, info_frame, marbles_left, mode=Themes.DARK):
        marbles_str = f'{marbles_left: >3}'
        
        first_d = self._render_didget(marbles_str[0])
        second_d = self._render_didget(marbles_str[1])
        third_d = self._render_didget(marbles_str[2])
        
        c = style.WHITE
        if mode == Themes.LIGHT:
            c = style.BLACK

        left_padding = 6
        lp = " " * left_padding

        lines = []
        lines.append(list(f'{c}{lp}   __  ______   ___  ___  __  ____   {first_d[0]} {second_d[0]} {third_d[0]}{style.RESET}'))
        lines.append(list(f'{c}{lp}  /  |/  / _ | / _ \\/ _ )/ / / __/   {first_d[1]} {second_d[1]} {third_d[1]}{style.RESET}'))
        lines.append(list(f'{c}{lp} / /|_/ / __ |/ , _/ _  / /___\\ \\     {first_d[2]} {second_d[2]} {third_d[2]}{style.RESET}'))
        lines.append(list(f'{c}{lp}/_/  /_/_/ |_/_/|_/____/____/___/     {first_d[3]} {second_d[3]} {third_d[3]}{style.RESET}'))
        lines.append(list(f'{c}{lp}                                      {first_d[4]} {second_d[4]} {third_d[4]}{style.RESET}'))
        lines.append(list(f'{c}{lp}                                      {style.RESET}'))
        
        starting_line = info_frame['line']
        for line in lines:
            info_frame['frame'][starting_line] = line
            starting_line += 1
        info_frame['line'] = starting_line
        
        return info_frame
    
    def _render_terminal(self, board):
        board_str = ""
        for row in board:
            row_str = ""
            for cell in row:
                if cell == MarbleSlotStates.EMPTY.value:
                    row_str += " . "
                elif cell == MarbleSlotStates.MARBLE.value:
                    row_str += " O "
                elif cell == MarbleSlotStates.INVALID.value:
                    row_str += "   "
            board_str += row_str + "\n"
        return board_str
    
    def _render_num_moves(self, info_frame, num_moves, mode=Themes.DARK):
        num_moves_str = f'{num_moves: >5}'
        
        first_d = self._render_didget(num_moves_str[0])
        second_d = self._render_didget(num_moves_str[1])
        third_d = self._render_didget(num_moves_str[2])
        fourth_d = self._render_didget(num_moves_str[3])
        fifth_d = self._render_didget(num_moves_str[4])
        
        c = style.WHITE
        if mode == Themes.LIGHT:
            c = style.BLACK
            
        left_padding = 6
        lp = " " * left_padding

        lines = []
        lines.append(list(f'{c}{lp}   __  _______ _   __________  _  {first_d[0]} {second_d[0]} {third_d[0]} {fourth_d[0]} {fifth_d[0]}{style.RESET}'))
        lines.append(list(f'{c}{lp}  /  |/  / __ \\ | / / __/ __/ (_) {first_d[1]} {second_d[1]} {third_d[1]} {fourth_d[1]} {fifth_d[1]}{style.RESET}'))
        lines.append(list(f'{c}{lp} / /|_/ / /_/ / |/ / _/_\\ \\  _    {first_d[2]} {second_d[2]} {third_d[2]} {fourth_d[2]} {fifth_d[2]}{style.RESET}'))
        lines.append(list(f'{c}{lp}/_/  /_/\\____/|___/___/___/ (_)   {first_d[3]} {second_d[3]} {third_d[3]} {fourth_d[3]} {fifth_d[3]}{style.RESET}'))
        lines.append(list(f'{c}{lp}                                  {first_d[4]} {second_d[4]} {third_d[4]} {fourth_d[4]} {fifth_d[4]}{style.RESET}'))
        
        starting_line = info_frame['line']
        for line in lines:
            info_frame['frame'][starting_line] = line
            starting_line += 1
        info_frame['line'] = starting_line
        
        return info_frame
    
    def _render_didget(self, d):
        out = []
        
        if not isinstance(d, str):
            raise ValueError("d must be a string.")
        
        if len(d) > 1:
            raise ValueError("d must be a single character.")
        
        if d == '-':
            out.append("     ")
            out.append(" ____")
            out.append("/___/")
            out.append("     ")
            out.append("     ")
            
        elif d == '0':
            out.append("  ___ ")
            out.append(" / _ \\")
            out.append("/ // /")
            out.append("\\___/ ")
            out.append("      ")
            
        elif d == '1':
            out.append("  ___")
            out.append(" <  /")
            out.append(" / / ")
            out.append("/_/  ")
            out.append("     ")
            
        elif d == '2':
            out.append("   ___ ")
            out.append("  |_  |")
            out.append(" / __/ ")
            out.append("/____/ ")
            out.append("       ")
        
        elif d == '3':
            out.append("   ____")
            out.append("  |_  /")
            out.append(" _/_ < ")
            out.append("/____/ ")
            out.append("       ")
        
        elif d == '4':
            out.append("  ____")
            out.append(" / / /")
            out.append("/_  _/")
            out.append(" /_/  ")
            out.append("      ")
            
        elif d == '5':
            out.append("   ____")
            out.append("  / __/")
            out.append(" /__ \\\ ")
            out.append("/____/ ")
            out.append("       ")
        
        elif d == '6':
            out.append("  ____")
            out.append(" / __/")
            out.append("/ _ \\ ")
            out.append("\\___/ ")
            out.append("      ")
        
        elif d == '7':
            out.append(" ____")
            out.append("/_  /")
            out.append(" / / ")
            out.append("/_/  ")
            out.append("     ")
        
        elif d == '8':
            out.append("  ___ ")
            out.append(" ( _ )")
            out.append("/ _  |")
            out.append("\\___/ ")
            out.append("      ")
        
        elif d == '9':
            out.append("  ___ ")
            out.append(" / _ \\")
            out.append(" \\_, /")
            out.append("/___/ ")
            out.append("      ")
        
        else:
            out.append("      ")
            out.append("      ")
            out.append("      ")
            out.append("      ")
            out.append("      ")
        
        return out
    
    def close(self):
        return
        