#!/usr/bin/env python3

ACTION_MOVE_UP = 0
ACTION_MOVE_RIGHT = 1
ACTION_MOVE_DOWN = 2
ACTION_MOVE_LEFT = 3
ALL_ACTIONS = [ACTION_MOVE_UP, ACTION_MOVE_RIGHT, ACTION_MOVE_DOWN, ACTION_MOVE_LEFT]

class CliffWalkingModel:

    def __init__(self):
        self.reset()
        return

    def reset(self):
        self.x = 0
        self.y = 3
        self.time = 0
        return

    def decode_state(self, state):
        column = state % 12
        row = (state - column) // 12
        return (row, column)

    def encode_state(self, row, column):
        state = row * 12 + column
        return state
    
    def ACTIONS(self, state):
        """Not allowed to move outside of the box, otherwise allowed."""
        row, column = self.decode_state(state)
        actions = []
        if column > 0:
            actions.append(ACTION_MOVE_LEFT)
        if column < 11:
            actions.append(ACTION_MOVE_RIGHT)
        if row > 0:
            actions.append(ACTION_MOVE_UP)
        if row < 3:
            actions.append(ACTION_MOVE_DOWN)
        return actions

    def GOAL_TEST(self, state):
        row, column = self.decode_state(state)
        return row == 3 and column == 11

    def RESULT(self, state, action):
        row, column = self.decode_state(state)
        if action == ACTION_MOVE_UP:
            row = max(0, row - 1)
        elif action == ACTION_MOVE_RIGHT:
            column = min(11, column + 1)
        elif action == ACTION_MOVE_LEFT:
            column = max(0, column - 1)
        elif action == ACTION_MOVE_DOWN:
            row = min(3, row + 1)
        else:
            raise Exception("Unexpected action: {}".format(action))
        
        if row == 3 and 0 < column < 11:
            row = 3
            column = 0

        state1 = self.encode_state(row, column)
        return state1