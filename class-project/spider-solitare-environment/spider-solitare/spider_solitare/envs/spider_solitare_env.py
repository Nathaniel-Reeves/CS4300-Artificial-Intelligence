import gymnasium
from gymnasium import spaces
from spider_solitare.envs.spider_solitare_model import SpiderSolitareModel
from spider_solitare.envs.spider_solitare_model import SpiderSolitareState
from copy import deepcopy
import os
import logging

from . import cards


class SpiderSolitareEnv(gymnasium.Env):

    metadata = {
        "render_modes": ["none", "ansi"],
        "render_fps": 1,
    }

    def __init__(self, seed=None, render_mode=None, num_suits=4, hide_obs=True, theme="dark"):
        
        # Validate num_suits to 4, 2, or 1
        if num_suits not in [4, 2, 1]:
            raise ValueError("num_suits must be 4, 2, or 1.")
        
        self.seed = seed
        
        self.render_mode = render_mode
        self._num_decks = 2
        self._num_suits = num_suits
        self._num_ranks = 13
        self._num_piles = 10
        self._num_completed_suits = 8
        self._hide_obs = hide_obs
        self._theme = theme
        self._state = SpiderSolitareState(self._num_suits)
        
        # Card space inclues the rank(int), suit(int), and visibility(binary) of a card
        card_space = spaces.MultiDiscrete([self._num_ranks + 1, self._num_suits + 1, 2])
        
        # Bank space inclues 1 pile that can hold 0 to 104 card_spaces
        bank_space = spaces.Sequence(card_space, stack=True)
        
        # Pile space inclues 10 piles that pile that can hold 0 to 104 card_spaces
        pile_space = spaces.Sequence(card_space, stack=True)
        piles_space = spaces.Dict({f"pile_{i+1}": pile_space for i in range(self._num_piles)})
        
        # Completed suit space inclues 8 piles that can hold 0 to 13 cards
        completed_suit_space = spaces.Sequence(card_space, stack=True)
        completed_suit_spaces = spaces.Dict({f"completed_suit_{i+1}": completed_suit_space for i in range(self._num_completed_suits)})
        
        # Hand space inclues 1 pile that can hold 0 to 13 cards
        hand_space = spaces.Sequence(card_space)

        self.observation_space = spaces.Dict({
            "bank": bank_space,
            "completed_suits": completed_suit_spaces,
            "hand": hand_space,
            "piles": piles_space,
            "pickup_pile_index": spaces.Discrete(self._num_piles + 1),
            "num_moves": spaces.Discrete(600),
            "score": spaces.Discrete(2000, start=-999)
        })
        
        self.action_space = spaces.Discrete((self._num_piles*2) + 1)

        return

    def reset(self, seed=None, options=None):
        # super().reset(seed=seed)
        self.seed = seed
        self.state = SpiderSolitareState(self._num_suits)
        self.state.deal(seed=self.seed)

        self.render()

        observation = self.state.observation
        hidden_obs = self.hide_observation(observation)
        info = {}
        
        if self._hide_obs:
            hidden_obs = self.hide_observation(observation)
            return hidden_obs, info
        return observation, info

    def step(self, action):
        state = self.state
        
        model = SpiderSolitareModel()
        obs = state.observation
        
        valid_actions = model.ACTIONS(obs)
        if action not in valid_actions:
            if action != 0:
                print(f"Action {action} is not valid. Valid actions are {valid_actions}.")
            score = model.STEP_COST(state.observation, action, state.observation)
            terminated = True
            info = {}
            return obs, score, terminated, False, info
        
        new_obs = model.RESULT(obs, action)
        state1 = SpiderSolitareState(self._num_suits)
        state1.observation = new_obs
        self.state = state1
        
        observation = self.state.observation
        reward = model.STEP_COST(state.observation, action, state1.observation)
        terminated = model.GOAL_TEST(state1.observation) or not model.ACTIONS(state1.observation)
        info = {}
        
        self.render()
        if self._hide_obs:
            hidden_obs = self.hide_observation(observation)
            return hidden_obs, reward, terminated, False, info
        return observation, reward, terminated, False, info
    
    def hide_observation(self, observation):
        hidden_observation = observation.copy()
        for key in hidden_observation.keys():
            if key == "bank":
                hidden_observation[key] = self.hide_bank(hidden_observation[key])
            if key == 'piles':
                hidden_observation[key] = self.hide_piles(hidden_observation[key])
        return hidden_observation
    
    def hide_bank(self, bank):
        hidden_bank = deepcopy(bank)
        for card in hidden_bank:
            card[0] = 0
            card[1] = 0
            card[2] = 0
        return hidden_bank
    
    def hide_piles(self, piles):
        copy_piles = piles.copy()
        for key in piles.keys():
            copy_piles[key] = self.hide_pile(copy_piles[key])
        return copy_piles
        
    def hide_pile(self, pile):
        copy_pile = deepcopy(pile)
        # iterate though pile in reverse order
        for i in range(len(copy_pile)-1, -1, -1):
            # if first card is hidden and there are not cards in the hand, unhide first card
            if i == len(copy_pile)-1 and copy_pile[i][2] == 0 and len(self.state.observation['hand']) == 0:
                copy_pile[i][2] = 1
                continue
            # if card is hidden and not first card, hide card
            if copy_pile[i][2] == 0:
                copy_pile[i][0] = 0
                copy_pile[i][1] = 0
                copy_pile[i][2] = 0
        return copy_pile

    def render(self):
        if self.render_mode == "ansi":
            print(self._render_text())
        return

    def _render_text(self):
        # clear screen, if logging level is set to warning
        if logging.getLogger().getEffectiveLevel() == logging.WARNING:
            os.system('cls' if os.name == 'nt' else 'clear')
        
        game_frame = self._build_game_frame()
        info_frame = self._build_info_frame()
        
        info_frame = self._render_title(info_frame, mode=self._theme)
        info_frame = self._render_score(info_frame, mode=self._theme)
        info_frame = self._render_num_moves(info_frame, mode=self._theme)
        info_frame = self._render_epilouge(info_frame, mode=self._theme)
        
        # Game
        game_frame = self._render_completed_piles_and_bank(game_frame, mode=self._theme)
        game_frame = self._render_piles(game_frame, mode=self._theme)
        game_frame = self._render_hand(game_frame, mode=self._theme)
        
        # place the game frame to the left of the info frame
        max_lines = max(len(game_frame['frame']), len(info_frame['frame']))
        for i in range(max_lines):
            if i >= len(game_frame['frame']):
                game_frame['frame'].append([" " for _ in range(59)])
            if i >= len(info_frame['frame']):
                info_frame['frame'].append([])
            game_frame['frame'][i] += info_frame['frame'][i]
        
        left_padding = 3
        lp = " " * left_padding
        
        out = ''
        for row in game_frame['frame']:
            out += f'{lp}' + "".join(row) + "\n"
            
        return out
    
    def _build_game_frame(self):
        width = 59
        height = 20
        
        frame = []
        for i in range(height):
            row = []
            for j in range(width):
                row.append(' ')
            frame.append(row)
        
        d = {
            'line': 0,
            'frame': frame,
        }
        
        return d
    
    def _build_info_frame(self):
        height = 50
        
        frame = []
        for i in range(height):
            row = []
            frame.append(row)
        
        d = {
            'line': 0,
            'frame': frame,
        }
        
        return d
    
    def _render_title(self, info_frame, mode='dark'):
        
        c = style.WHITE
        if mode == 'light':
            c = style.BLACK

        left_padding = 6
        lp = " " * left_padding

        lines = []
        lines.append(list(f'{c}{lp}   ____     _    __          ____     ___ __              {style.RESET}'))
        lines.append(list(f'{c}{lp}  / __/__  (_)__/ /__ ____  / __/__  / (_) /____ ________ {style.RESET}'))
        lines.append(list(f'{c}{lp} _\\ \\/ _ \\/ / _  / -_) __/ _\\ \\/ _ \\/ / / __/ _ `/ __/ -_){style.RESET}'))
        lines.append(list(f'{c}{lp} /___/ .__/_/\\_,_/\\__/_/   /___/\\___/_/_/\\__/\_,_/_/  \\__/ {style.RESET}'))
        lines.append(list(f'{c}{lp}     /_/                                                    {style.RESET}'))
        lines.append(list(f'{c}{lp}=========================================================================={style.RESET}'))
        
        starting_line = info_frame['line']
        for line in lines:
            info_frame['frame'][starting_line] = line
            starting_line += 1
        info_frame['line'] = starting_line
        
        return info_frame
    
    def _render_epilouge(self, info_frame, mode='dark'):
        c = style.WHITE
        if mode == 'light':
            c = style.BLACK

        left_padding = 6
        lp = " " * left_padding

        lines = []
        lines.append(list(f'{c}{lp}=========================================================================={style.RESET}'))
        lines.append(list(f'{c}{lp}     Created by: Nathaniel Reeves in November of 2024 for a CS 4300{style.RESET}'))
        lines.append(list(f'{c}{lp}     Artificial Inteligence class project at Utah Tech University.{style.RESET}'))
        lines.append(list(f'{c}{lp}=========================================================================={style.RESET}'))
        
        starting_line = info_frame['line']
        for line in lines:
            info_frame['frame'][starting_line] = line
            starting_line += 1
        info_frame['line'] = starting_line
        
        return info_frame
    
    def _render_score(self, info_frame, mode='dark'):
        score = self.state.observation['score']
        
        score_str = f'{score: >5}'
        
        first_d = self._render_didget(score_str[0])
        second_d = self._render_didget(score_str[1])
        third_d = self._render_didget(score_str[2])
        forth_d = self._render_didget(score_str[3])
        fifth_d = self._render_didget(score_str[4])
        
        c = style.WHITE
        if mode == 'light':
            c = style.BLACK

        left_padding = 8
        lp = " " * left_padding

        lines = []
        lines.append(list(f'{c}{lp}   _____________  ___  ____  _  {first_d[0]} {second_d[0]} {third_d[0]} {forth_d[0]} {fifth_d[0]}{style.RESET}'))
        lines.append(list(f'{c}{lp}  / __/ ___/ __ \/ _ \/ __/ (_) {first_d[1]} {second_d[1]} {third_d[1]} {forth_d[1]} {fifth_d[1]}{style.RESET}'))
        lines.append(list(f'{c}{lp} _\ \/ /__/ /_/ / , _/ _/  _    {first_d[2]} {second_d[2]} {third_d[2]} {forth_d[2]} {fifth_d[2]}{style.RESET}'))
        lines.append(list(f'{c}{lp}/___/\___/\____/_/|_/___/ (_)   {first_d[3]} {second_d[3]} {third_d[3]} {forth_d[3]} {fifth_d[3]}{style.RESET}'))
        lines.append(list(f'{c}{lp}                                {first_d[4]} {second_d[4]} {third_d[4]} {forth_d[4]} {fifth_d[4]}{style.RESET}'))
        
        starting_line = info_frame['line']
        for line in lines:
            info_frame['frame'][starting_line] = line
            starting_line += 1
        info_frame['line'] = starting_line
        
        return info_frame
    
    def _render_num_moves(self, info_frame, mode='dark'):
        num_moves = self.state.observation['num_moves']
        
        num_moves_str = f'{num_moves: >5}'
        
        first_d = self._render_didget(num_moves_str[0])
        second_d = self._render_didget(num_moves_str[1])
        third_d = self._render_didget(num_moves_str[2])
        fourth_d = self._render_didget(num_moves_str[3])
        fifth_d = self._render_didget(num_moves_str[4])
        
        c = style.WHITE
        if mode == 'light':
            c = style.BLACK
            
        left_padding = 6
        lp = " " * left_padding

        lines = []
        lines.append(list(f'{c}{lp}   __  _______ _   __________  _  {first_d[0]} {second_d[0]} {third_d[0]} {fourth_d[0]} {fifth_d[0]}{style.RESET}'))
        lines.append(list(f'{c}{lp}  /  |/  / __ \ | / / __/ __/ (_) {first_d[1]} {second_d[1]} {third_d[1]} {fourth_d[1]} {fifth_d[1]}{style.RESET}'))
        lines.append(list(f'{c}{lp} / /|_/ / /_/ / |/ / _/_\ \  _    {first_d[2]} {second_d[2]} {third_d[2]} {fourth_d[2]} {fifth_d[2]}{style.RESET}'))
        lines.append(list(f'{c}{lp}/_/  /_/\____/|___/___/___/ (_)   {first_d[3]} {second_d[3]} {third_d[3]} {fourth_d[3]} {fifth_d[3]}{style.RESET}'))
        lines.append(list(f'{c}{lp}                                  {first_d[4]} {second_d[4]} {third_d[4]} {fourth_d[4]} {fifth_d[4]}{style.RESET}'))
        
        starting_line = info_frame['line']
        for line in lines:
            info_frame['frame'][starting_line] = line
            starting_line += 1
        info_frame['line'] = starting_line
        
        return info_frame
    
    def _render_completed_piles_and_bank(self, game_frame, mode='dark'):
        completed_suits = self.state.observation['completed_suits']
        row = []
        for key in completed_suits.keys():
            if (len(completed_suits[key]) == 0):
                card = cards.render_empty_pile(mode=mode)
            else:
                card = cards.render_card(completed_suits[key][0][0], completed_suits[key][0][1], mode=mode)
            row.append(card)
        
        if len(self.state.observation['bank']) == 0:
            bank = cards.render_empty_pile()
        else:
            bank = cards.render_pile_count(len(self.state.observation['bank'])//10, mode=mode)
        
        num_bg = 1 # bank gap
        bg = " " * (6 * num_bg)
        
        lines = []
        lines.append(list("".join(card[0] for card in row) + bg + "".join(bank[0])))
        lines.append(list("".join(card[1] for card in row) + bg + "".join(bank[1])))
        lines.append(list("".join(card[2] for card in row) + bg + "".join(bank[2])))
        
        starting_line = game_frame['line']
        for line in lines:
            game_frame['frame'][starting_line][0:59] = line
            starting_line += 1
        game_frame['line'] = starting_line
        
        return game_frame
    
    def _render_hand(self, game_frame, mode='dark'):
        hand = self.state.observation['hand']
        rendered_hand = []
        if len(hand) == 0:
            card = cards.render_empty_pile(mode=mode)
            rendered_hand.append(card)
        else:
            for card in hand:
                rendered_hand.append(cards.render_card(card[0], card[1], mode=mode))
        
        lines = []
        lines.append(list("".join(card[0] for card in rendered_hand)))
        lines.append(list("".join(card[1] for card in rendered_hand)))
        lines.append(list("".join(card[2] for card in rendered_hand)))
        
        starting_line = game_frame['line'] + 2
        
        for line in lines:
            if starting_line > len(game_frame['frame']) - 1:
                for _ in range(3):
                    game_frame['frame'].append([" " for _ in range(59)])
            game_frame['frame'][starting_line][0:59] = line
            starting_line += 1
        game_frame['line'] = starting_line
        
        return game_frame
    
    def _render_piles(self, game_frame, mode='dark'):
        piles = self.state.observation['piles']
        
        if self._hide_obs:
            hidden_obs = self.hide_observation(self.state.observation)
            piles = hidden_obs['piles']
        
        i = 0
        cols = []
        while True:
            row = []
            emply_col_count = 0
            for key in piles.keys():
                pile = piles[key]
                if i == 0 and len(pile) == 0:
                    card = cards.render_empty_pile(mode=mode)
                    row.append(card)
                    emply_col_count += 1
                    continue
                if i < len(pile):
                    card = pile[i]
                    row.append(cards.render_card(card[0], card[1], mode=mode))
                else:
                    row.append(cards.render_blank_space())
                    emply_col_count += 1
            cols.append(row)
            if emply_col_count == len(piles):
                break
            i += 1
        
        starting_line = game_frame['line'] + 3
        for row in cols:
            lines = []
            
            lines.append(list("".join([card[0] for card in row])))
            lines.append(list("".join([card[1] for card in row])))
            lines.append(list("".join([card[2] for card in row])))
            
            for line in lines:
                if starting_line > len(game_frame['frame']) - 1:
                    for _ in range(3):
                        game_frame['frame'].append([" " for _ in range(59)])
                
                game_frame['frame'][starting_line][0:59] = line
                starting_line += 1
            game_frame['line'] = starting_line
        
        return game_frame
    
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
            out.append("\___/ ")
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
            out.append(" /__ \\ ")
            out.append("/____/ ")
            out.append("       ")
        
        elif d == '6':
            out.append("  ____")
            out.append(" / __/")
            out.append("/ _ \ ")
            out.append("\___/ ")
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
            out.append("\___/ ")
            out.append("      ")
        
        elif d == '9':
            out.append("  ___ ")
            out.append(" / _ \\")
            out.append(" \_, /")
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