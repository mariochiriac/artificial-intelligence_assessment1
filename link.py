# link.py
# Moves link towards the gold
# Summons one of the algorithms in search.py. Algorithms generate a path towards the goal
# Returns moves stored in a path until all of the gold is found
# Last modified by Mario Chiriac at 20/03/2025

from search import GameSearchProblem, SEARCH_ALGORITHMS
from utils import Pose, Directions

class Link:
    def __init__(self, dungeon, algorithmType):
        # Initialize Link with the game world (dungeon) and the chosen algorithm type.
        self.gameWorld = dungeon
        
        # Validate algorithm type, defaulting to Depth-First Search (DFS) if invalid.
        self.algorithmType = algorithmType if algorithmType in SEARCH_ALGORITHMS else 1
        
        # Initialize path tracking and step tracking variables.
        self.path = []
        self.path_index = 0
        self.steps_taken = 0
        self.replans = 0 
        self.total_nodes = 0  # Tracks total nodes expanded across all searches

    def makeMove(self):
        # Determine the next move based on the current path or replan if necessary.
        current_location = self.gameWorld.getLinkLocation()
        
        # Check if Link is currently on a gold tile.
        if self.has_gold(current_location):
            print("Gold found at current location!")
            return None  # End move if gold is found
        
        # If the path is empty or completed, plan a new path.
        if not self.path or self.path_index >= len(self.path):
            print("Path empty or completed. Planning new path...")
            start = (current_location.x, current_location.y)
            
            # Retrieve all remaining gold locations.
            remaining_gold = set((g.x, g.y) for g in self.gameWorld.getGoldLocation())
            
            # If no gold remains, terminate.
            if not remaining_gold:
                print("All gold collected!")
                return None
            
            # Formulate a search problem and apply the selected algorithm.
            problem = GameSearchProblem(self.gameWorld, start, remaining_gold)
            search_func = SEARCH_ALGORITHMS[self.algorithmType]
            self.path = search_func(problem)
            self.path_index = 0
            self.replans += 1
            
            # Track the number of nodes expanded during this search.
            self.total_nodes += problem.nodes_expanded
            
            # If no path is found, print an error and terminate.
            if not self.path:
                print("No path found to any gold!")
                return None
            
            print(f"New path planned with algorithm {self.algorithmType}: {self.path}")
        
        # Retrieve the next move from the path.
        next_move = self.path[self.path_index]
        
        # Simulate the next move to check for dangers.
        next_loc = Pose(current_location.x, current_location.y)
        
        if next_move == Directions.NORTH:
            next_loc.y += 1
        elif next_move == Directions.SOUTH:
            next_loc.y -= 1
        elif next_move == Directions.EAST:
            next_loc.x += 1
        elif next_move == Directions.WEST:
            next_loc.x -= 1
        
        # Check for danger or sensory cues
        if self.gameWorld.isDangerous(next_loc.x, next_loc.y) or self.gameWorld.isSmelly(next_loc) or self.gameWorld.isWindy(next_loc):
            print("Next move is risky! Finding a safe move...")
            safe_move = self.findSafeMove(current_location)
            if safe_move:
                self.steps_taken += 1
                print(f"Steps taken: {self.steps_taken}, Replans: {self.replans}")
                return safe_move
            print("No safe moves available.")
            return None

        self.path_index += 1
        self.steps_taken += 1
        print(f"Steps taken: {self.steps_taken}, Replans: {self.replans}")
        return next_move

    def findSafeMove(self, current_location):
        # Identify all possible moves from the current location.
        possible_moves = self.getActions(current_location)
        if not possible_moves:
            return None

        # Track Wumpus positions to avoid them.
        wumpus_positions = set((w.x, w.y) for w in self.gameWorld.wLoc)
        safe_moves = []

        # Retrieve the last move to minimize unnecessary turns.
        last_move = self.path[self.path_index - 1] if self.path_index > 0 else None

        for action in possible_moves:
            # Simulate the new location for the move.
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

            # Ensure the move is safe by avoiding Wumpuses and adjacent danger.
            if (new_pos not in wumpus_positions and
                not any(abs(new_loc.x - wx) + abs(new_loc.y - wy) == 1 for wx, wy in wumpus_positions)):
                
                # Prefer moves that lead directly to gold.
                if self.gameWorld.isGlitter(new_loc):
                    return action
                
                # Calculate move score based on distance to the nearest gold and turn penalties.
                gold_locs = self.gameWorld.getGoldLocation()
                if gold_locs:
                    nearest_gold = min(gold_locs, key=lambda g: abs(g.x - new_loc.x) + abs(g.y - new_loc.y))
                    dist = abs(nearest_gold.x - new_loc.x) + abs(nearest_gold.y - new_loc.y) # Heuristic (Manhattan Distance towards Gold)
                    turn_penalty = 0 if last_move == action else 1
                    score = dist + turn_penalty
                    safe_moves.append((score, action))
        
        # Select the safest move with the lowest score.
        if safe_moves:
            safe_moves.sort(key=lambda x: x[0])
            return safe_moves[0][1]
        return None

    def has_gold(self, location):
        # Check if the current location contains gold.
        return any(location.x == g.x and location.y == g.y for g in self.gameWorld.getGoldLocation())

    def getActions(self, location):
        # Determine all safe moves from the current location.
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