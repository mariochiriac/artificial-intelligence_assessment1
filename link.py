# link.py
# Defines Link's behavior in the Wumpus World game.
# Written by: Simon Parsons
# Last Modified: 25/08/20
# Optimized by: Mario Chiriac - March 2025

import random
import utils
import config
from utils import Pose, Directions
from search import Search

class Link:
    def __init__(self, dungeon, algorithmType):
        self.gameWorld = dungeon
        self.algorithmType = algorithmType
        self.search = Search(self.gameWorld)
        self.allGold = set((gold.x, gold.y) for gold in self.gameWorld.getGoldLocation())
        self.path = []
        self.path_index = 0

    def makeMove(self):
        """Execute Link's next move, replanning if necessary."""
        if not self.path or self.path_index >= len(self.path):
            print("Path empty or completed. Planning new path...")
            start = self.gameWorld.getLinkLocation()
            self.path = self.search.find_path(self.algorithmType, start, self.allGold)
            self.path_index = 0
            if not self.path:
                print("No path found!")
                return None

        current_location = self.gameWorld.getLinkLocation()
        next_move = self.path[self.path_index]
        print(f"Next move: {next_move}")

        # Simulate next location
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

        # Dynamic hazard avoidance
        if config.dynamic and (self.gameWorld.isSmelly(next_loc) or
                               self.gameWorld.isWindy(next_loc) or
                               (next_loc.x == current_location.x and next_loc.y == current_location.y)):
            print(f"{next_move} is risky or blocked! Finding safe move...")
            safe_move = self.findSafeMove(current_location)
            if safe_move:
                self.path[self.path_index] = safe_move
                self.path_index += 1
                return safe_move
            else:
                print("No safe moves, proceeding anyway!")
                self.path_index += 1
                return next_move

        self.path_index += 1
        return next_move

    def findSafeMove(self, current_location):
        """Find a safe move, prioritizing gold proximity."""
        possible_moves = self.search.getActions(current_location)
        if not possible_moves:
            return None

        wumpus_positions = set((w.x, w.y) for w in self.gameWorld.wLoc)
        safe_moves = []

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
            if (new_pos not in wumpus_positions and
                not any(abs(new_loc.x - wx) + abs(new_loc.y - wy) == 1 for wx, wy in wumpus_positions)):
                if self.gameWorld.isGlitter(new_loc):
                    return action
                gold_locs = self.gameWorld.getGoldLocation()
                nearest_gold = min(gold_locs, key=lambda g: abs(g.x - new_loc.x) + abs(g.y - new_loc.y))
                dist = abs(nearest_gold.x - new_loc.x) + abs(nearest_gold.y - new_loc.y)
                turn_penalty = 0 if last_move == action else 1
                score = dist + turn_penalty
                safe_moves.append((score, action))

        if safe_moves:
            safe_moves.sort(key=lambda x: x[0])
            return safe_moves[0][1]
        return None

    def has_gold(self, location):
        return any(location.x == g.x and location.y == g.y for g in self.gameWorld.getGoldLocation())