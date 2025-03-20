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

from search import GameSearchProblem, SEARCH_ALGORITHMS
from utils import Pose, Directions

class Link:
    def __init__(self, dungeon, algorithmType):
        # Initialize Link with the game world and algorithm type.
        self.gameWorld = dungeon
        
        # Validate and set the algorithm type (Defaults to DFS if invalid)
        self.algorithmType = algorithmType if algorithmType in SEARCH_ALGORITHMS else 1
        
        # Track the planned path and current index within the path
        self.path = []
        self.path_index = 0

    def makeMove(self):
        # Determine the next move based on the current path or replan if necessary.
        current_location = self.gameWorld.getLinkLocation()
        
        # Check if the current location contains gold
        if self.has_gold(current_location):
            print("Gold found at current location!")
            return None  # Return None to signify gold collection
        
        # Replan if the path is empty or completed
        if not self.path or self.path_index >= len(self.path):
            print("Path empty or completed. Planning new path...")
            start = (current_location.x, current_location.y)
            
            # Get all remaining gold locations
            remaining_gold = set((g.x, g.y) for g in self.gameWorld.getGoldLocation())
            
            if not remaining_gold:
                print("All gold collected!")
                return None
            
            # Formulate the search problem and apply the selected algorithm
            problem = GameSearchProblem(self.gameWorld, start, remaining_gold)
            search_func = SEARCH_ALGORITHMS[self.algorithmType]
            self.path = search_func(problem)
            self.path_index = 0
            
            if not self.path:
                print("No path found to any gold!")
                return None
            
            print(f"New path planned with algorithm {self.algorithmType}: {self.path}")
        
        # Get the next planned move from the path
        next_move = self.path[self.path_index]
        
        # Simulate movement to check if the next move is safe
        next_loc = Pose(current_location.x, current_location.y)
        
        if next_move == Directions.NORTH:
            next_loc.y += 1
        elif next_move == Directions.SOUTH:
            next_loc.y -= 1
        elif next_move == Directions.EAST:
            next_loc.x += 1
        elif next_move == Directions.WEST:
            next_loc.x -= 1
        
        # If the next move is dangerous, attempt to find a safer alternative
        if self.gameWorld.isDangerous(next_loc.x, next_loc.y):
            print("Next move is dangerous! Finding a safe move...")
            safe_move = self.findSafeMove(current_location)
            
            if safe_move:
                print(f"Safe move found: {safe_move}")
                return safe_move
            else:
                print("No safe moves available. Staying put.")
                return None
        
        # Execute the next move and increment the path index
        self.path_index += 1
        return next_move

    def findSafeMove(self, current_location):
        # Find a safe move, prioritizing proximity to gold and avoiding Wumpuses.
        possible_moves = self.getActions(current_location)
        if not possible_moves:
            return None

        # Track Wumpus positions to ensure safe moves
        wumpus_positions = set((w.x, w.y) for w in self.gameWorld.wLoc)
        safe_moves = []

        # Track the last move to avoid unnecessary turning
        last_move = self.path[self.path_index - 1] if self.path_index > 0 else None

        for action in possible_moves:
            # Simulate the new position for the given action
            new_loc = Pose(current_location.x, current_location.y)
            
            if action == Directions.NORTH:
                new_loc.y += 1
            elif action == Directions.SOUTH:
                new_loc.y -= 1
            elif action == Directions.EAST:
                new_loc.x += 1
            elif action == Directions.WEST:
                new_loc.x -= 1

            new_pos = (new_loc.x, new_loc.y)

            # Ensure the move avoids Wumpuses and is not adjacent to them
            if (new_pos not in wumpus_positions and
                not any(abs(new_loc.x - wx) + abs(new_loc.y - wy) == 1 for wx, wy in wumpus_positions)):
                
                # Prioritize moves that find gold
                if self.gameWorld.isGlitter(new_loc):
                    return action
                
                # Calculate the distance to the nearest gold to score the move
                gold_locs = self.gameWorld.getGoldLocation()
                if gold_locs:
                    nearest_gold = min(gold_locs, key=lambda g: abs(g.x - new_loc.x) + abs(g.y - new_loc.y))
                    dist = abs(nearest_gold.x - new_loc.x) + abs(nearest_gold.y - new_loc.y)
                    turn_penalty = 0 if last_move == action else 1
                    score = dist + turn_penalty
                    safe_moves.append((score, action))
        
        # Select the safest move with the lowest score
        if safe_moves:
            safe_moves.sort(key=lambda x: x[0])
            return safe_moves[0][1]
        return None

    def has_gold(self, location):
        # Check if the given location contains gold.
        return any(location.x == g.x and location.y == g.y for g in self.gameWorld.getGoldLocation())

    def getActions(self, location):
        # Get all possible actions from the current location, ensuring safety.
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