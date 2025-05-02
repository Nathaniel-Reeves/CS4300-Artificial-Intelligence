#!/usr/bin/env python3

import cliff_model as cliff
import logging

# MAKE CLASS Node
# MAKE CLASS Frontier

class Agent1:

    def __init__(self):
        """required, with no arguments to initialize correctly"""
        self.model = cliff.CliffWalkingModel()
        self.max_depth = 13
        self.actions = []
        return

    def reset(self):
        """required"""
        self.model.reset()
        self.max_depth = 13
        self.actions = []
        return

    def dfs(self, s0):
        logging.info("DFS: s0: ", s0)
        goal_node = None
        # NODE: (state, parent_node, action, depth)
        frontier = [ (s0, None, None, 0) ]
        while len(frontier) > 0:
            node = frontier.pop()
            state, parent, action, depth = node
            if self.model.GOAL_TEST(state):
                goal_node = node
                break
            elif depth >= self.max_depth:
                # do not generate children
                continue
            for action in self.model.ACTIONS(state):
                state1 = self.model.RESULT(state, action)
                node1 = (state1, node, action, depth+1)
                frontier.append(node1)
        action_sequence = []
        if goal_node:
            node = goal_node
            while node[1] is not None and node[1][1] is not None:
                node = node[1]
                action_sequence.append(node[2])
            if node[1][1] is None:
                action_sequence.append(node[2])
        logging.info("Action sequence: {}".format(action_sequence))
        logging.info("DFS: actions: ", action_sequence)
        return action_sequence

    def agent_function(self, state):
        """required"""
        max_depth = self.max_depth
        if len(self.actions) == 0:
            self.actions = self.dfs(state)
        if len(self.actions) == 0:
            raise Exception("DFS Search failed.")
        action = self.actions.pop()
        if action is None:
            logging.warn("state: {}".format(state))
            raise Exception("Oof!")
        return action
    