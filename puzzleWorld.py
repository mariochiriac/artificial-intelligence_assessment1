# puzzleWorld.py
# Represents the puzzle version of the Wumpus World.
# Written by: Simon Parsons
# Last Modified: 17/12/24

import random
import config
import utils
from search import Search
from world import World
from utils import Pose, Directions, State

class PuzzleWorld(World):
    def __init__(self):
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
        self.status = State.PLAY
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        self.plan = []

    def buildPlan(self, for_char, goal, algorithm_type):
        """Build a plan using DFS (1) or A* (2) from Search class."""
        if for_char == 0:
            start = (self.lLoc.x, self.lLoc.y)
            goal_loc = (goal.lLoc.x, goal.lLoc.y)
            format_move = lambda action: [action, 0, 0]  # Link move
        else:
            start = (self.wLoc[for_char - 1].x, self.wLoc[for_char - 1].y)
            goal_loc = (goal.wLoc[for_char - 1].x, goal.wLoc[for_char - 1].y)
            format_move = lambda action: [0, action, 0] if for_char == 1 else [0, 0, action]  # Wumpus move

        if algorithm_type == 1:
            plan = Search.dfs_path(start, goal_loc, self.maxX, self.maxY)
        elif algorithm_type == 2:
            plan = Search.astar_path(start, goal_loc, self.maxX, self.maxY)
        else:
            plan = Search.dfs_path(start, goal_loc, self.maxX, self.maxY)  # Default to DFS

        if plan:
            self.plan = list(map(format_move, plan))
        else:
            print(f"No solution found for character {for_char}")
            self.plan = []

    def isSolved(self, goal):
        if utils.sameLink(self, goal) and utils.sameWumpus(self, goal):
            self.status = State.WON
            print("Puzzle Over! Wumpus and Link match.")
            return True
        return False

    def makeAMove(self, goal):
        if self.plan:
            move = self.plan.pop(0)  # Changed to pop(0) for FIFO
            print(move)
            self.takeStep(move)
        else:
            print("Nothing to do!")

    def takeStep(self, move):
        if move[0] != 0:
            print("Moving Link")
            direction = move[0]
            if direction == Directions.NORTH and self.lLoc.y < self.maxY:
                self.lLoc.y += 1
            elif direction == Directions.SOUTH and self.lLoc.y > 0:
                self.lLoc.y -= 1
            elif direction == Directions.EAST and self.lLoc.x < self.maxX:
                self.lLoc.x += 1
            elif direction == Directions.WEST and self.lLoc.x > 0:
                self.lLoc.x -= 1
        else:
            for i in range(1, len(self.wLoc) + 1):
                if move[i] != 0:
                    print(f"Moving Wumpus {i-1}")
                    direction = move[i]
                    j = i - 1
                    if direction == Directions.NORTH and self.wLoc[j].y < self.maxY:
                        self.wLoc[j].y += 1
                    elif direction == Directions.SOUTH and self.wLoc[j].y > 0:
                        self.wLoc[j].y -= 1
                    elif direction == Directions.EAST and self.wLoc[j].x < self.maxX:
                        self.wLoc[j].x += 1
                    elif direction == Directions.WEST and self.wLoc[j].x > 0:
                        self.wLoc[j].x -= 1