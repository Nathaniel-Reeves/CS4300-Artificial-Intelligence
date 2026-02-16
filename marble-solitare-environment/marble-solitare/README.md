Marble Solitaire Environment
-------------------------

# Description

The state is a standard setup for a marble solitaire game.
The goal is to remove marbles by jumping over them until only one marble remains on the board.

# Observation Space

An observation returns a dictionary with the following information:

- "board": A 7x7 numpy array representing the game board
  - -1 = Invalid position (off the board)
  - 0 = Empty slot (available for landing)
  - 1 = Marble present
- "marbles_left": Count of remaining marbles on the board
- "moves_made": Total number of moves taken

## Board Layout

### English Board (default)
```
    O O O
    O O O
O O O O O O O
O O O . O O O  (center starts empty)
O O O O O O O
    O O O
    O O O
```

### European Board
```
    O O O
  O O O O O
O O O O O O O
O O O . O O O  (center starts empty)
O O O O O O O
  O O O O O
    O O O
```

# Action Space

Action space is represented by a tuple: `(from_y, from_x, to_y, to_x)`

- `from_y`, `from_x`: Position of the marble to move (0-indexed)
- `to_y`, `to_x`: Destination position (must be 2 spaces away in cardinal direction)

Valid moves:
- Must jump over exactly one adjacent marble
- Landing position must be empty
- Can only move in cardinal directions (up, down, left, right)
- The jumped marble is removed from the board

# Starting State

The starting state represents a standard marble solitaire setup:
- 7x7 board with corners marked as invalid positions
- All valid positions contain marbles except the center position
- English board: 32 marbles initially
- European board: 36 marbles initially
- Center position (3, 3) starts empty

# Rewards

The reward system is designed to encourage solving the puzzle efficiently:

- `-1` per move: Each move has a cost of -1 to encourage fewer moves
- Goal state (1 marble remaining): Episode terminates successfully

The reward structure penalizes each move, so agents are incentivized to:
- Reach the goal state (1 marble) as quickly as possible
- Minimize the number of moves taken

# Episode End

The episode terminates when:
- **Success**: Only 1 marble remains on the board (goal reached)
- **Failure**: No valid moves remain but more than 1 marble is on the board

The episode can be truncated with a maximum step limit if needed via
`gymnasium.make()` parameters.

# Board Types

Two board types are available via the `type` parameter:
- `MarbleSolitareBoardTypes.ENGLISH`: Standard English cross pattern (32 initial marbles)
- `MarbleSolitareBoardTypes.EUROPEAN`: European octagonal pattern (36 initial marbles)

# Rendering

Terminal rendering is available showing:
- Board state with `.` for empty, `O` for marbles, and spaces for invalid positions
- Marbles remaining count
- Number of moves taken
- ASCII art title and statistics (when using `_render_text()`)
