# puzzleWorld.py
#
# A file that represents a puzzle version of the Wumpus World, keeping
# track of the position of the Wumpus and Link.
#
# Written by: Simon Parsons
# Last Modified: 17/12/24

import random
import config
import utils
import copy
import search
from search import Search
from node import Node
from world import World
from utils import Pose
from utils import Directions
from utils import State

class PuzzleWorld(World):

    def __init__(self):
        # 
        self.maxX = config.worldLength - 1
        self.maxY = config.worldBreadth - 1
        self.wLoc = []
        self.locationList = []
        for i in range(config.numberOfWumpus):
            newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
            self.wLoc.append(newLoc)
            self.locationList.append(newLoc)
        newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
        self.lLoc = newLoc
        self.locationList.append(newLoc)
        self.pLoc = []
        self.gLoc = []
        self.status = utils.State.PLAY
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        self.plan = []

        
        # A plan
        # self.plan = [[Directions.EAST, 0, 0], [0, Directions.NORTH, 0], [0, 0, Directions.NORTH]]
    
    def buildPlan(self, for_char, goal, algorithm_type):
        """Build a plan using DFS (1) or A* (2)."""
        if for_char == 0:
            start = self.lLoc
            goal_loc = goal.lLoc
            format_move = lambda action: [action, 0, 0]  # Link move
        else:
            start = self.wLoc[for_char - 1]
            goal_loc = goal.wLoc[for_char - 1]
            format_move = lambda action: [0, action, 0] if for_char == 1 else [0, 0, action]  # Wumpus move

        if algorithm_type == 1:
            self.plan = Search.dfs(start, goal_loc, self.maxX, self.maxY, format_move)
        else:  # algorithm_type == 2
            self.plan = Search.astar(start, goal_loc, self.maxX, self.maxY, format_move)
        if not self.plan:
            print(f"No solution found for character {for_char}")
         
    def buildPlanDFS(self):
        start = self.gameWorld.getLinkLocation()  # Start position
        node = Node(start)  # x, y of Link
        
        stack = [node]  # Stack for DFS
        explored = set()
        
        while stack:
            node = stack.pop()
            
            # Skip if already visited
            if (node.location.x, node.location.y) in explored:
                continue
            
            explored.add((node.location.x, node.location.y))
            final_path.append(node)  # Add node to final path
            
            # Expand possible moves from current location
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
                
                if (child.location.x, child.location.y) not in explored:
                    stack.append(child)

    #
    # Methods
    #
    # These are the functions that are used to update and report on
    # puzzle information.
    def isSolved(self, goal):
        if utils.sameLink(self, goal) and utils.sameWumpus(self, goal):
            self.status = utils.State.WON
            print("Puzzle Over! Wumpus and Link match.")
            return True
        else:
            return False


    # A single move is to shift Link or one Wumpus in one direction.
    #
    # This relies on having something in self.plan. Once this has been
    # reduced to [], this code will just print a message each time step.
    #
    # This is where you should start writing your solution to the
    # puzle problem.
    def makeAMove(self, goal):
        if self.plan:
            move = self.plan.pop()
            print(move)
            self.takeStep(move)
        else:
            print("Nothing to do!")


    # A move is a list of the directions that [Link, Wumpus1, Wumpus2,
    # ...] move in.  takeStep decodes these and makes the relevant
    # change to the state. Basically it looks for the first list
    # element that is non-zero and interprets this as a
    # direction. Movements that exceed the limits of the world have no
    # effect.
    def takeStep(self, move):
        # Move Link
        print(f"Move 0: {move[0]}, move 1: {move[1]}")
        if move[0] != 0:
            print("Moving Link")
            direction = move[0]
            if direction == Directions.NORTH:
                if self.lLoc.y < self.maxY:
                    self.lLoc.y = self.lLoc.y + 1
            
            if direction == Directions.SOUTH:
                if self.lLoc.y > 0:
                    self.lLoc.y = self.lLoc.y - 1
                
            if direction == Directions.EAST:
                if self.lLoc.x < self.maxX:
                    self.lLoc.x = self.lLoc.x + 1
                
            if direction == Directions.WEST:
                if self.lLoc.x > 0:
                    self.lLoc.x = self.lLoc.x - 1
        # Otherwise move the relevant Wumpus
        else:
            for i in range(1, len(self.wLoc) + 1):
                if move[i] != 0:
                    print("Moving Wumpus", i-1)
                    direction = move[i]
                    j = i - 1
                    if direction == Directions.NORTH:
                        if self.wLoc[j].y < self.maxY:
                            self.wLoc[j].y = self.wLoc[j].y + 1
            
                    if direction == Directions.SOUTH:
                        if self.wLoc[j].y > 0:
                            self.wLoc[j].y = self.wLoc[j].y - 1
                
                    if direction == Directions.EAST:
                        if self.wLoc[j].x < self.maxX:
                            self.wLoc[j].x = self.wLoc[j].x + 1
                
                    if direction == Directions.WEST:
                        if self.wLoc[j].x > 0:
                            self.wLoc[j].x = self.wLoc[j].x - 1


