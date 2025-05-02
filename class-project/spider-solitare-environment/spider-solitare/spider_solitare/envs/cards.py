SPADE = '♠'
HEART = '♥'
DIAMOND = '♦'
CLUB = '♣'

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

def render_card(rank, suit, mode='dark'):
    color1 = None
    color2 = None
    color3 = None
    if mode == 'light':
        color1 = style.BLUE
        color2 = style.RED
        color3 = style.BLACK
    elif mode == 'dark':
        color1 = style.YELLOW
        color2 = style.CYAN
        color3 = style.WHITE
    
    color = color1
    
    if suit == 1:
        suit = SPADE
    elif suit == 2:
        suit = HEART
        color = color2
    elif suit == 3:
        suit = DIAMOND
        color = color2
    elif suit == 4:
        suit = CLUB
    
    if rank == 1:
        rank = 'A'
    elif rank == 11:
        rank = 'J'
    elif rank == 12:
        rank = 'Q'
    elif rank == 13:
        rank = 'K'
    
    if rank == 0 or suit == 0:
        rank = 'X'
        suit = 'X'
        color = color3
    
    card = (f'{color}╭───╮ {style.RESET}', f'{color}│{rank: <2}{suit}│ {style.RESET}', f'{color}╰───╯ {style.RESET}')
    return card

def render_empty_pile(mode='dark'):
    color1 = None
    color2 = None
    color3 = None
    if mode == 'light':
        color1 = style.RED
        color2 = style.BLUE
        color3 = style.BLACK
    elif mode == 'dark':
        color1 = style.YELLOW
        color2 = style.CYAN
        color3 = style.WHITE
    return (f'{color3}╭───╮ {style.RESET}', f'{color3}│   │ {style.RESET}', f'{color3}╰───╯ {style.RESET}')

def render_pile_count(count=0, mode='dark'):
    color1 = None
    color2 = None
    color3 = None
    if mode == 'light':
        color1 = style.RED
        color2 = style.BLUE
        color3 = style.BLACK
    elif mode == 'dark':
        color1 = style.YELLOW
        color2 = style.CYAN
        color3 = style.WHITE
    return (f'{color3}╭───╮ {style.RESET}', f'{color3}│ {count: <2}│ {style.RESET}', f'{color3}╰───╯ {style.RESET}')

def render_blank_space():
    return ('      ', '      ', '      ')

def print_single_card(card):
    print(card[0])
    print(card[1])
    print(card[2])
    return

if __name__ == '__main__':
    card = render_card(10, 1)
    print_single_card(card)
    card = render_card(6, 2)
    print_single_card(card)
    card = render_card(2, 3)
    print_single_card(card)
    card = render_card(12, 4)
    print_single_card(card)
    