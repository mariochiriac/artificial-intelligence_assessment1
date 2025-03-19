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
# Optimized by: Mario Chiriac - March 2025

import heapq
import random
import utils
import config
from node import Node  # created Node class for easier algorithm management
from utils import Pose, Directions

class Link:
    # added chosen algorithm type
    def __init__(self, dungeon, algorithmType):
        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon
        self.algorithmType = algorithmType
        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        self.allGold = set((gold.x, gold.y) for gold in self.gameWorld.getGoldLocation())
        self.gold_collected = set()

        # Establish a path that will be determined by an algorithm
        self.path = []
        self.path_index = 0

    # Executes Link's next move, dodging hazards dynamically
    def makeMove(self):
        # If we haven’t created a path yet, create one.
        if not self.path:
            self.chooseAlgorithm(self.algorithmType)

        # If the path index is out of bounds, replan a new path.
        if self.path_index >= len(self.path):
            print("Path Finished or out of index. Recalculating path...")
            self.chooseAlgorithm(self.algorithmType)
            self.path_index = 0
            if not self.path:
                print("No new path found!")
                return None

        current_location = self.gameWorld.getLinkLocation()
        next_move = self.path[self.path_index]
        print(f"next move: {next_move}")

        # Simulate next location with bounds clipping.
        next_loc = Pose()
        next_loc.x = current_location.x
        next_loc.y = current_location.y
        if next_move == Directions.NORTH:
            next_loc.y = min(current_location.y + 1, self.gameWorld.maxY)
        elif next_move == Directions.SOUTH:
            next_loc.y = max(current_location.y - 1, 0)
        elif next_move == Directions.EAST:
            next_loc.x = min(current_location.x + 1, self.gameWorld.maxX)
        elif next_move == Directions.WEST:
            next_loc.x = max(current_location.x - 1, 0)

        # Debug Wumpus positions.
        wumpus0 = self.gameWorld.wLoc[0]
        wumpus1 = self.gameWorld.wLoc[1]
        print(f"next location: {(next_loc.x, next_loc.y)} | current loc: {(current_location.x, current_location.y)}")
        print(f"wumpus 0: {(wumpus0.x, wumpus0.y)} | wumpus 1: {(wumpus1.x, wumpus1.y)}")

        # Check if next move is risky or blocked.
        if config.dynamic == True:
            if (self.gameWorld.isSmelly(next_loc) or 
                self.gameWorld.isWindy(next_loc) or 
                (next_loc.x == current_location.x and next_loc.y == current_location.y)):
                print(f"{next_move} is too close or hits edge! Dodging...")
                safe_move = self.findSafeMove(current_location)
                if safe_move:
                    # Replace the move at current index if it exists, otherwise append.
                    if self.path_index < len(self.path):
                        self.path[self.path_index] = safe_move
                    else:
                        self.path.append(safe_move)
                    self.path_index += 1
                    return safe_move
                else:
                    print("No safe moves, proceeding cautiously!")
                    self.path_index += 1
                    return next_move

        # Safe move, proceed as planned.
        self.path_index += 1
        return self.path[self.path_index - 1]

    # Function that chooses an algorithm based on given type
    def chooseAlgorithm(self, algorithmType):
        if self.algorithmType == 1:
            print("Depth First Search Initiated")
            self.path = self.depthFirstSearch()
        elif self.algorithmType == 2:
            print("Breadth First Search Initiated")
            self.path = self.breadthFirstSearch()
        elif self.algorithmType == 3:
            print("Uniform Cost Search Initiated")
            self.path = self.uniformCostSearch()
        elif self.algorithmType == 4:
            self.path = self.greedySearch()
        else:
            print("No Algorithm Chosen. Default Algorithm: Depth First Search")
            self.path = self.depthFirstSearch()

    # If wumpus or pit is nearby, finds safe move. Prioritises isGlitter(), which checks if gold is nearby
    def findSafeMove(self, current_location):
        possible_moves = self.getActions(current_location)
        if not possible_moves:
            return None

        # Cache Wumpus positions for quick checks
        wumpus_positions = set((w.x, w.y) for w in self.gameWorld.wLoc)
        safe_moves = []

        # Get last move for turn penalty
        last_move = self.path[self.path_index - 1] if self.path_index > 0 else None

        for action in possible_moves:
            new_loc = Pose()
            new_loc.x = current_location.x
            new_loc.y = current_location.y
            if action == Directions.NORTH:
                new_loc.y += 1
            elif action == Directions.SOUTH:
                new_loc.y -= 1
            elif action == Directions.EAST:
                new_loc.x += 1
            elif action == Directions.WEST:
                new_loc.x -= 1

            new_pos = (new_loc.x, new_loc.y)
            # Skip if move lands on or next to Wumpus
            if (new_pos not in wumpus_positions and 
                not any(abs(new_loc.x - wx) + abs(new_loc.y - wy) == 1 for wx, wy in wumpus_positions)):
                # Prioritize moves near gold with isGlitter
                if self.gameWorld.isGlitter(new_loc):
                    return action  # faster win as gold is closer
                # Fallback: score by distance + turn penalty
                gold_locs = self.gameWorld.getGoldLocation()
                nearest_gold = min(gold_locs, key=lambda g: abs(g.x - new_loc.x) + abs(g.y - new_loc.y))
                dist = abs(nearest_gold.x - new_loc.x) + abs(nearest_gold.y - new_loc.y)
                turn_penalty = 0 if last_move == action else 1
                score = dist + turn_penalty
                safe_moves.append((score, action))

        if safe_moves:
            safe_moves.sort(key=lambda x: x[0])  # Lowest score = best move
            return safe_moves[0][1]
        return None

    # Depth First Search to find all gold
    def depthFirstSearch(self):
        start = self.gameWorld.getLinkLocation()
        node = Node(start)
        
        stack = [node]
        explored = set()
        final_path = []
        
        while stack:
            node = stack.pop()
            if (node.location.x, node.location.y) in explored:
                continue
            
            explored.add((node.location.x, node.location.y))
            final_path.append(node.action)
            
            current_pos = (node.location.x, node.location.y)
            if current_pos in self.allGold and current_pos not in self.gold_collected:
                self.gold_collected.add(current_pos)
                print(f"Gold found at {node.location.x}, {node.location.y}")
            
            if self.gold_collected == self.allGold and current_pos in self.allGold:
                return [action for action in final_path if action is not None]
            
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
                if (child.location.x, child.location.y) not in explored:
                    stack.append(child)
        
        print("Failed to find all gold")
        return []

    # Breadth First Search for shortest path to all gold
    def breadthFirstSearch(self):
        current_gold = self.allGold  # Set of gold positions
        start = self.gameWorld.getLinkLocation()
        start_node = Node(start, gold_collected=set())
        
        queue = [start_node]
        visited = {}  # keys are (position, frozenset(gold_collected))
        
        while queue:
            node = queue.pop(0)
            current_pos = (node.location.x, node.location.y)
            
            # Update collected gold for this node if present at the current position
            new_collected = node.gold_collected.copy()
            if current_pos in current_gold and current_pos not in new_collected:
                new_collected.add(current_pos)
                print(f"Collected gold at {current_pos}")
            
            # Check for termination: all gold collected
            if new_collected == current_gold:
                node.gold_collected = new_collected
                return self.recoverPlan(node)
            
            # Build state key including gold collected info
            state_key = (current_pos, frozenset(new_collected))
            if state_key in visited:
                continue
            visited[state_key] = True
            
            # Expand neighbors with the updated gold collection state
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
                child.gold_collected = new_collected.copy()
                child_state = ((child.location.x, child.location.y),
                               frozenset(child.gold_collected))
                if child_state not in visited:
                    queue.append(child)
                    
        print("Failed to find all gold")
        return []


    # Uniform Cost Search for optimal cost to all gold
    # Uniform Cost Search for optimal cost to all gold, considering hazards and glitter
    def uniformCostSearch(self):
        # Fetch live gold locations from the world
        current_gold = set((g.x, g.y) for g in self.gameWorld.getGoldLocation())
        if not current_gold:
            print("All gold already collected!")
            return []

        start = self.gameWorld.getLinkLocation()
        start_node = Node(start, gold_collected=set())

        priority_queue = []
        heapq.heappush(priority_queue, (0, 0, start_node))  # (cost, tiebreaker, node)

        # Track visited states: (position, collected_gold)
        explored = {}

        while priority_queue:
            current_cost, _, current_node = heapq.heappop(priority_queue)
            current_pos = (current_node.location.x, current_node.location.y)
            collected = current_node.gold_collected

            # Termination: Check if all gold has been collected
            if collected == current_gold:
                return self.recoverPlan(current_node)

            # State validation
            state_key = (current_pos, frozenset(collected))
            if state_key in explored and explored[state_key] <= current_cost:
                continue
            explored[state_key] = current_cost

            # Gold collection check
            new_collected = collected.copy()
            if current_pos in current_gold and current_pos not in collected:
                new_collected.add(current_pos)
                print(f"Collected gold at {current_pos}")

            # Generate child nodes
            for action in self.getActions(current_node.location):
                child = self.createChildNode(current_node, action)
                child.gold_collected = new_collected.copy()

                # Cost calculation: Base movement cost
                child_cost = current_cost + 1

                # Hazard penalties
                if self.gameWorld.isSmelly(child.location):
                    child_cost += 10  # Penalty for Wumpus proximity
                if self.gameWorld.isWindy(child.location):
                    child_cost += 8   # Penalty for pits

                # Removed the glitter reward to avoid negative step costs
                # If you want to prioritize glitter locations, consider a non-negative alternative.

                # Validate child state
                child_state = ((child.location.x, child.location.y),
                               frozenset(child.gold_collected))
                if child_state not in explored or explored[child_state] > child_cost:
                    tiebreaker = id(child)  # Unique identifier for tie-breaking
                    heapq.heappush(priority_queue, (child_cost, tiebreaker, child))

        print(f"No path found for {len(current_gold)} remaining gold!")
        return []

    def greedySearch(self):
        # Determine current gold positions.
        current_gold = set((g.x, g.y) for g in self.gameWorld.getGoldLocation())
        if not current_gold:
            print("All gold already collected!")
            return []

        # Define a simple Manhattan distance heuristic.
        def heuristic(node):
            remaining = current_gold - node.gold_collected
            if not remaining:
                return 0
            hx, hy = node.location.x, node.location.y
            return min(abs(gx - hx) + abs(gy - hy) for gx, gy in remaining)

        start = self.gameWorld.getLinkLocation()
        start_node = Node(start, gold_collected=set())
        initial_h = heuristic(start_node)

        # Priority queue holds tuples: (heuristic, tie_breaker, node)
        priority_queue = []
        heapq.heappush(priority_queue, (initial_h, 0, start_node))

        # Explored dictionary tracks states by (position, collected_gold)
        explored = {}

        while priority_queue:
            current_h, _, current_node = heapq.heappop(priority_queue)
            current_pos = (current_node.location.x, current_node.location.y)
            collected = current_node.gold_collected.copy()

            # If gold is at the current position, collect it.
            if current_pos in current_gold and current_pos not in collected:
                collected.add(current_pos)
                print(f"Collected gold at {current_pos}")

            # Check if all gold has been collected.
            if collected == current_gold:
                current_node.gold_collected = collected
                return self.recoverPlan(current_node)

            # Create a state key using the current position and collected gold.
            state_key = (current_pos, frozenset(collected))
            if state_key in explored and explored[state_key] <= current_h:
                continue
            explored[state_key] = current_h

            # Expand successors.
            for action in self.getActions(current_node.location):
                child = self.createChildNode(current_node, action)
                child.gold_collected = collected.copy()
                child_h = heuristic(child)
                child_state = ((child.location.x, child.location.y),
                               frozenset(child.gold_collected))
                if child_state not in explored or explored[child_state] > child_h:
                    tiebreaker = id(child)
                    heapq.heappush(priority_queue, (child_h, tiebreaker, child))

        print("No path found for remaining gold!")
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
        return Node(new_location, parent, action, new_depth, gold_collected=parent.gold_collected.copy())

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