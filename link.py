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

import heapq
from inspect import stack
from queue import PriorityQueue
import world
import random
import utils
from node import Node # created Node class for easier algorithm management
from utils import Pose, Directions

class Link():

    # added chosen algorithm type
    def __init__(self, dungeon, algorithmType):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon
        self.algorithmType = algorithmType

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
            if self.algorithmType == 1:
                self.path = self.depthFirstSearch()
            elif self.algorithmType == 2:
                self.path = self.breadthFirstSearch()
            elif self.algorithmType == 3:
                self.path = self.uniformCostSearch()
            else: print("No Algorithm Chosen. Default Algorithm: Depth First Search")
            
        
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

    # Breadth First Search
    def breadthFirstSearch(self):
        start = self.gameWorld.getLinkLocation()  # Start position
        node = Node(start)  # x, y of Link
        allGold = set((gold.x, gold.y) for gold in self.gameWorld.getGoldLocation())  # Store all gold locations
        
        queue = [node]  # Queue for Breadth First Search
        explored = set()
        gold_collected = set()  # Track collected gold
        final_path = []  # Complete path to collect all gold
        
        while queue:
            node = queue.pop(0) # element dequeued from queue
            
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
                    queue.append(child)
        
        print("Failed to find all gold")
        return []

    def uniformCostSearch(self):
        # establish start node
        start = self.gameWorld.getLinkLocation()
        node = Node(start)
        allGold = set((gold.x, gold.y) for gold in self.gameWorld.getGoldLocation())
        
        priority_queue = []
        heapq.heappush(priority_queue, (node.cost, node)) # push node to priority queue, along with its cost
        
        # keep track of explored nodes and their cost, gold and the final path
        explored = {}
        gold_collected = set()
        final_path = []
        
        while priority_queue:
            current_cost, node = heapq.heappop(priority_queue) # pop a node from the heap
            
            # if node was already explored and with a lower cost, skip
            if (node.location.x, node.location.y) in explored and explored[(node.location.x, node.location.y)] <= current_cost: # checks node in explored, along with the cost
                continue
            
            # Mark the current location with its cost
            explored[(node.location.x, node.location.y)] = current_cost
            final_path.append(node)
        
            # Check if the current node has gold
            if (node.location.x, node.location.y) in allGold:
                gold_collected.add((node.location.x, node.location.y))
                print(f"Gold found at {node.location.x}, {node.location.y} with cost {current_cost}")
            
                # If all gold pieces are collected, recover and return the path
                if gold_collected == allGold:
                    return self.recoverPlan(node)
        
            # Expand all possible moves from the current node
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
            
                # For uniform cost (every move costs 1), update the child cost:
                child.cost = node.cost + 1
            
                # If you have varying move costs, you can adjust the cost like:
                # child.cost = node.cost + step_cost
                # where step_cost is determined by the specific action or terrain.
            
                # Only add the child if this is the best path found so far
                if (child.location.x, child.location.y) not in explored or explored[(child.location.x, child.location.y)] > child.cost:
                    heapq.heappush(priority_queue, (child.cost, child))
    
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
        new_depth = parent.cost + 1
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