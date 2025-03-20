# node.py

import utils
        
class Node:
    def __init__(self, location, parent=None, action=None, cost=0, gold_collected=None):
        self.location = location  # Pose (x, y)
        self.parent = parent      # Parent node (for path recovery)
        self.action = action      # Action taken (NORTH, SOUTH, EAST, WEST)
        self.cost = cost          # Depth in search tree
        self.gold_collected = gold_collected if gold_collected is not None else set()

    def isGoal(self, gold):
        return (self.location.x, self.location.y) == (gold.x, gold.y)

    def __eq__(self, other):
        return self.location.x == other.location.x and self.location.y == other.location.y

    def __hash__(self):
        return hash((self.location.x, self.location.y))
