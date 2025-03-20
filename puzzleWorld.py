# puzzleWorld.py
#
# Represents the puzzle version of Wumpus World, managing positions of Link and Wumpuses.
#
# Written by: Simon Parsons
# Last Modified: 17/12/24

import random
import config
import utils
import copy
from world import World
from utils import Pose
from utils import Directions
from utils import State
from search import PuzzleSearchProblem, SEARCH_ALGORITHMS

class PuzzleWorld(World):

    def __init__(self):
        # Set world boundaries based on config (0-based, so subtract 1 from length/breadth)
        self.maxX = config.worldLength - 1
        self.maxY = config.worldBreadth - 1

        # List to track occupied positions and ensure uniqueness
        self.locationList = []

        # Initialize Wumpus positions randomly
        self.wLoc = []
        for i in range(config.numberOfWumpus):
            newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
            self.wLoc.append(newLoc)         # Add Wumpus position to list
            self.locationList.append(newLoc) # Mark position as used

        # Initialize Link’s position, ensuring it’s unique
        newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
        self.lLoc = newLoc
        self.locationList.append(newLoc)     # Mark Link’s position as used

        # Unused elements from the game version (pits and gold)
        self.pLoc = []
        self.gLoc = []
        
        # Set initial game state to active
        self.status = utils.State.PLAY

        # Define all possible movement directions
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

        # Start with an empty plan for moves
        self.plan = []

        # Count Steps
        self.steps = 0

    # Check if the current state matches the goal state
    def isSolved(self, goal):
        # Use utils.sameAs to compare positions of Link and Wumpuses
        if utils.sameAs(self, goal):
            self.status = utils.State.WON   # Mark as won if solved
            print("Puzzle Over!")
            return True
        return False

    # Build a movement plan for Link and Wumpuses to reach their goals
    def buildPlan(self, algorithm_type, goal):
        # Clear any existing plan
        self.plan = []
        
        # Validate algorithm type; fallback to DFS (1) if invalid
        algorithm_type = algorithm_type if algorithm_type in SEARCH_ALGORITHMS else 1
        search_func = SEARCH_ALGORITHMS[algorithm_type]     # Get the search function

        # Plan path for Link to its goal position
        start = (self.lLoc.x, self.lLoc.y)
        goal_loc = (goal.lLoc.x, goal.lLoc.y)
        problem = PuzzleSearchProblem(start, goal_loc, self.maxX, self.maxY)
        path = search_func(problem)  # Compute path using chosen algorithm
        if path:
            self.plan.extend([[action, 0, 0] for action in path])  # Add Link’s moves
        else:
            print("No solution found for Link")

        # Plan paths for each Wumpus to their goal positions
        for i in range(len(self.wLoc)):
            start = (self.wLoc[i].x, self.wLoc[i].y)
            goal_loc = (goal.wLoc[i].x, goal.wLoc[i].y)
            problem = PuzzleSearchProblem(start, goal_loc, self.maxX, self.maxY)
            path = search_func(problem)  # Compute path for this Wumpus
            if path:
                if i == 0:
                    self.plan.extend([[0, action, 0] for action in path])  # Wumpus 0 moves
                elif i == 1:
                    self.plan.extend([[0, 0, action] for action in path])  # Wumpus 1 moves
            else:
                print(f"No solution found for Wumpus {i}")

        # Log the plan result
        if self.plan:
            print(f"Plan built with algorithm {algorithm_type}: {self.plan}")
        else:
            print("No complete plan found")

    # Execute the next move from the plan
    def makeAMove(self, goal):
        # Check if there’s a move to make
        if self.plan:
            move = self.plan.pop(0)     # Take first move to maintain order
            #print(move)                 # Show the move being executed
            self.takeStep(move)         # Apply the move
        else:
            print("Nothing to do!")     # No moves left in plan

    # Apply a single move to either Link or a Wumpus
    def takeStep(self, move):
        # Move Link if the first element is non-zero
        if move[0] != 0:
            print("Moving Link")
            direction = move[0]
            if direction == Directions.NORTH and self.lLoc.y < self.maxY:
                self.lLoc.y += 1    # Move up if within bounds
            elif direction == Directions.SOUTH and self.lLoc.y > 0:
                self.lLoc.y -= 1    # Move down if within bounds
            elif direction == Directions.EAST and self.lLoc.x < self.maxX:
                self.lLoc.x += 1    # Move right if within bounds
            elif direction == Directions.WEST and self.lLoc.x > 0:
                self.lLoc.x -= 1    # Move left if within bounds
        # Otherwise, move the appropriate Wumpus
        else:
            for i in range(1, len(self.wLoc) + 1):
                if move[i] != 0:
                    print(f"Moving Wumpus {i-1}")
                    direction = move[i]
                    j = i - 1           # Index of Wumpus in wLoc
                    if direction == Directions.NORTH and self.wLoc[j].y < self.maxY:
                        self.wLoc[j].y += 1     # Move Wumpus up
                    elif direction == Directions.SOUTH and self.wLoc[j].y > 0:
                        self.wLoc[j].y -= 1     # Move Wumpus down
                    elif direction == Directions.EAST and self.wLoc[j].x < self.maxX:
                        self.wLoc[j].x += 1     # Move Wumpus right
                    elif direction == Directions.WEST and self.wLoc[j].x > 0:
                        self.wLoc[j].x -= 1     # Move Wumpus left