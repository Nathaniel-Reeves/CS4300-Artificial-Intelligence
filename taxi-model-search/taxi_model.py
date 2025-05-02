#!/usr/bin/env python3
import logging

# Actions
ACTION_MOVE_DOWN = 0
ACTION_MOVE_UP = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_LEFT = 3
ACTION_PICKUP = 4
ACTION_DROPOFF = 5
ALL_ACTIONS = [ACTION_MOVE_UP, ACTION_MOVE_RIGHT, ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_PICKUP, ACTION_DROPOFF]

# Passenger Locations
L_RED = 0
L_GREEN = 1
L_YELLOW = 2
L_BLUE = 3
L_TAXI = 4

# Destinations
D_RED = 0
D_GREEN = 1
D_YELLOW = 2
D_BLUE = 3

class TaxiDrivingModel:

    def __init__(self):
        self.reset()
        self.most_recent_action = None
        return

    def reset(self):
        self.x = 0
        self.y = 3
        self.time = 0
        return

    def decode_state(self, state):
        destination = state % 4
        passenger_location = (state - destination) // 4 % 5
        taxi_col = (state - (passenger_location * 4) - destination) // 20 % 5
        taxi_row = (state - (taxi_col * 5) - (passenger_location * 4) - destination) // 100 % 5
        logging.debug(f"Decoded state: {state} -> ({taxi_row}, {taxi_col}, {passenger_location}, {destination})")
        return (taxi_row, taxi_col, passenger_location, destination)

    def encode_state(self, taxi_row, taxi_col, passenger_location, destination):
        state = ((taxi_row * 5 + taxi_col) * 5 + passenger_location) * 4 + destination
        return state
    
    def ACTIONS(self, state):
        """Not allowed to move outside of the box, otherwise allowed."""
        taxi_row, taxi_col, passenger_location, destination = self.decode_state(state)
        key = f"{taxi_col}_{taxi_row}"
        #  0 1 2 3 4
        # +---------+
        # |R: | : :G| 0
        # | : | : : | 1
        # | : : : : | 2
        # | | : | : | 3
        # |Y| : |B: | 4
        # +---------+
        valid_moves = {
            '0_0': [ACTION_MOVE_DOWN, ACTION_MOVE_RIGHT],
            '0_1': [ACTION_MOVE_DOWN, ACTION_MOVE_RIGHT, ACTION_MOVE_UP],
            '0_2': [ACTION_MOVE_DOWN, ACTION_MOVE_RIGHT, ACTION_MOVE_UP],
            '0_3': [ACTION_MOVE_DOWN, ACTION_MOVE_UP],
            '0_4': [ACTION_MOVE_UP],
            '1_0': [ACTION_MOVE_DOWN, ACTION_MOVE_LEFT],
            '1_1': [ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_MOVE_UP],
            '1_2': [ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_MOVE_UP, ACTION_MOVE_RIGHT],
            '1_3': [ACTION_MOVE_DOWN, ACTION_MOVE_UP, ACTION_MOVE_RIGHT],
            '1_4': [ACTION_MOVE_UP, ACTION_MOVE_RIGHT],
            '2_0': [ACTION_MOVE_RIGHT, ACTION_MOVE_DOWN],
            '2_1': [ACTION_MOVE_RIGHT, ACTION_MOVE_DOWN, ACTION_MOVE_UP],
            '2_2': [ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_MOVE_UP, ACTION_MOVE_RIGHT],
            '2_3': [ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_MOVE_UP],
            '2_4': [ACTION_MOVE_LEFT, ACTION_MOVE_UP],
            '3_0': [ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT],
            '3_1': [ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_MOVE_UP, ACTION_MOVE_RIGHT],
            '3_2': [ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_MOVE_UP, ACTION_MOVE_RIGHT],
            '3_3': [ACTION_MOVE_DOWN, ACTION_MOVE_UP, ACTION_MOVE_RIGHT],
            '3_4': [ACTION_MOVE_UP, ACTION_MOVE_RIGHT],
            '4_0': [ACTION_MOVE_LEFT, ACTION_MOVE_DOWN],
            '4_1': [ACTION_MOVE_LEFT, ACTION_MOVE_DOWN, ACTION_MOVE_UP],
            '4_2': [ACTION_MOVE_LEFT, ACTION_MOVE_DOWN, ACTION_MOVE_UP],
            '4_3': [ACTION_MOVE_LEFT, ACTION_MOVE_DOWN, ACTION_MOVE_UP],
            '4_4': [ACTION_MOVE_LEFT, ACTION_MOVE_UP]
        }
        actions = valid_moves[key]

        # RED STOP
        if taxi_row == 0 and taxi_col == 0 and passenger_location == L_RED:
            actions.append(ACTION_PICKUP)
        # GREEN STOP
        elif taxi_row == 0 and taxi_col == 4 and passenger_location == L_GREEN:
            actions.append(ACTION_PICKUP)
        # YELLOW STOP
        elif taxi_row == 4 and taxi_col == 0 and passenger_location == L_YELLOW:
            actions.append(ACTION_PICKUP)
        # BLUE STOP
        elif taxi_row == 4 and taxi_col == 3 and passenger_location == L_BLUE:
            actions.append(ACTION_PICKUP)
        
        # RED STOP
        if taxi_row == 0 and taxi_col == 0 and destination == L_RED and passenger_location == L_TAXI:
            actions.append(ACTION_DROPOFF)
        # GREEN STOP
        elif taxi_row == 0 and taxi_col == 4 and destination == L_GREEN and passenger_location == L_TAXI:
            actions.append(ACTION_DROPOFF)
        # YELLOW STOP
        elif taxi_row == 4 and taxi_col == 0 and destination == L_YELLOW and passenger_location == L_TAXI:
            actions.append(ACTION_DROPOFF)
        # BLUE STOP
        elif taxi_row == 4 and taxi_col == 3 and destination == L_BLUE and passenger_location == L_TAXI:
            actions.append(ACTION_DROPOFF)
        
        # if self.most_recent_action in actions:
        #     actions.remove(self.most_recent_action)

        return actions

    def GOAL_TEST(self, state):
        taxi_row, taxi_col, passenger_location, destination = self.decode_state(state)
        #  0 1 2 3 4
        # +---------+
        # |R: | : :G| 0
        # | : | : : | 1
        # | : : : : | 2
        # | | : | : | 3
        # |Y| : |B: | 4
        # +---------+
        
        if passenger_location != L_TAXI:
            # Pick up Passenger
            if passenger_location == L_RED and taxi_row == 0 and taxi_col == 0:
                return True
            elif passenger_location == L_GREEN and taxi_row == 0 and taxi_col == 4:
                return True
            elif passenger_location == L_YELLOW and taxi_row == 4 and taxi_col == 0:
                return True
            elif passenger_location == L_BLUE and taxi_row == 4 and taxi_col == 3:
                return True
            else:
                return False
        else:
            # Drop off Passenger
            if destination == D_RED and passenger_location == L_RED:
                return True
            elif destination == D_GREEN and passenger_location == L_GREEN:
                return True
            elif destination == D_YELLOW and passenger_location == L_YELLOW:
                return True
            elif destination == D_BLUE and passenger_location == L_BLUE:
                return True
            else:
                return False

    def RESULT(self, state, action):
        taxi_row, taxi_col, passenger_location, destination = self.decode_state(state)
        self.most_recent_action = action
        #  0 1 2 3 4
        # +---------+
        # |R: | : :G| 0
        # | : | : : | 1
        # | : : : : | 2
        # | | : | : | 3
        # |Y| : |B: | 4
        # +---------+
        if action == ACTION_MOVE_UP:
            taxi_row = max(0, taxi_row - 1)
        elif action == ACTION_MOVE_RIGHT:
            taxi_col = min(4, taxi_col + 1)
        elif action == ACTION_MOVE_LEFT:
            taxi_col = max(0, taxi_col - 1)
        elif action == ACTION_MOVE_DOWN:
            taxi_row = min(4, taxi_row + 1)
        elif action == ACTION_PICKUP:
            passenger_location = L_TAXI
        elif action == ACTION_DROPOFF:
            # RED STOP
            if taxi_row == 0 and taxi_col == 0 and passenger_location == L_TAXI:
                passenger_location = L_RED
            # GREEN STOP
            elif taxi_row == 0 and taxi_col == 4 and passenger_location == L_TAXI:
                passenger_location = L_GREEN
            # YELLOW STOP
            elif taxi_row == 4 and taxi_col == 0 and passenger_location == L_TAXI:
                passenger_location = L_YELLOW
            # BLUE STOP
            elif taxi_row == 4 and taxi_col == 3 and passenger_location == L_TAXI:
                passenger_location = L_BLUE
            else:
                logging.info(f"Unexpected DROPOFF action: {action}")
                raise Exception("Unexpected DROPOFF action: {}".format(action))
        else:
            logging.warn(f"Unexpected action: {action}")
            raise Exception("Unexpected action: {}".format(action))

        state1 = self.encode_state(taxi_row, taxi_col, passenger_location, destination)
        return state1