# link.py
#
# The code that defines the behaviour of Link.
#
# You should be able to write the code for a simple solution to the
# game version of the Wumpus World here, getting information about the
# game state from self.gameWorld, and using makeMove() to generate the
# next move.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20

from inspect import stack
import world
import random
import utils
from node import Node # created Node class for easier algorithm management
from utils import Pose, Directions

class Link():

    def __init__(self, dungeon):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        
        # Establish a path that will be determined by an algorithm
        self.path = []
        self.path_index = 0
        
    def makeMove(self):
        # This is the function you need to define
        #
        # For now we have a placeholder, which always moves Link
        # directly towards the gold.
        
        # if we haven't created a path yet, create one
        if not self.path:
            self.path = self.depthFirstSearch()
        
        if self.path_index == len(self.path):
            print("Path Finished")
            return

        # if index is smaller than length of path, continue along the path by incrementing path index
        if self.path_index < len(self.path):
            self.path_index += 1

        return self.path[self.path_index - 1]
        

    # Depth First Search
    def depthFirstSearch(self):
        start = self.gameWorld.getLinkLocation()  # Start position
        node = Node(start)  # x, y of Link
        allGold = set((gold.x, gold.y) for gold in self.gameWorld.getGoldLocation())  # Store all gold locations
        
        stack = [node]  # Stack for DFS
        explored = set()
        gold_collected = set()  # Track collected gold
        final_path = []  # Complete path to collect all gold
        
        while stack:
            node = stack.pop()
            
            # Skip if already visited
            if (node.location.x, node.location.y) in explored:
                continue
            
            explored.add((node.location.x, node.location.y))
            final_path.append(node)  # Add node to final path
            
            # Check if current node is gold
            if (node.location.x, node.location.y) in allGold:
                gold_collected.add((node.location.x, node.location.y))
                print(f"Gold found at {node.location.x}, {node.location.y}")
                
                # If all gold is collected, return path
                if gold_collected == allGold:
                    return self.recoverPlan(node)
            
            # Expand possible moves from current location
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
                
                if (child.location.x, child.location.y) not in explored:
                    stack.append(child)
        
        print("Failed to find all gold")
        return []


    # Functions that enables to get all possible directions from a location
    # Checks if a location is dangerous after applying directions
    def getActions(self, location):
        actions = []
    
        if location.y < self.gameWorld.maxY and not self.gameWorld.isDangerous(location.x, location.y + 1):
            actions.append(Directions.NORTH)
        if location.y > 0 and not self.gameWorld.isDangerous(location.x, location.y - 1):
            actions.append(Directions.SOUTH)
        if location.x < self.gameWorld.maxX and not self.gameWorld.isDangerous(location.x + 1, location.y):
            actions.append(Directions.EAST)
        if location.x > 0 and not self.gameWorld.isDangerous(location.x - 1, location.y):
            actions.append(Directions.WEST)

        return actions


    # creates new search nodes based on movement direction
    def createChildNode(self, parent, action):
        new_depth = parent.depth + 1
        new_location = Pose()
        
        new_location.x = parent.location.x
        new_location.y = parent.location.y

        if action == Directions.EAST:
            new_location.x += 1
        elif action == Directions.WEST:
            new_location.x -= 1
        elif action == Directions.NORTH:
            new_location.y += 1
        elif action == Directions.SOUTH:
            new_location.y -= 1

        return Node(new_location, parent, action, new_depth)
    
    # Extract Movement Path
        # trace back the path and return a sequence of moves.
    def recoverPlan(self, node):
        plan = []
        self.recoverPlanRecursive(node, plan)
        return plan

    def recoverPlanRecursive(self, node, plan):
        if node.parent:
            self.recoverPlanRecursive(node.parent, plan)
            plan.append(node.action)