# search.py
import heapq
from utils import Pose, Directions
from node import Node  # Assuming Node is defined in node.py

class Search:
    # Static methods for puzzle version (simple pathfinding)
    @staticmethod
    def dfs_path(start, goal, maxX, maxY):
        """DFS for puzzle: Find path from start to goal on a grid."""
        stack = [(start, [])]  # (position (x, y), path)
        visited = set()
        while stack:
            (x, y), path = stack.pop()
            if (x, y) == goal:
                return path
            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy, action in [(0, 1, Directions.NORTH), (0, -1, Directions.SOUTH),
                                       (1, 0, Directions.EAST), (-1, 0, Directions.WEST)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx <= maxX and 0 <= ny <= maxY:
                        stack.append(((nx, ny), path + [action]))
        return None

    @staticmethod
    def astar_path(start, goal, maxX, maxY):
        """A* for puzzle: Find optimal path from start to goal."""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        pq = [(0 + heuristic(start, goal), 0, start, [])]  # (f, g, position, path)
        visited = {}
        while pq:
            f, g, (x, y), path = heapq.heappop(pq)
            if (x, y) == goal:
                return path
            if (x, y) in visited and visited[(x, y)] <= g:
                continue
            visited[(x, y)] = g
            for dx, dy, action in [(0, 1, Directions.NORTH), (0, -1, Directions.SOUTH),
                                   (1, 0, Directions.EAST), (-1, 0, Directions.WEST)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx <= maxX and 0 <= ny <= maxY:
                    ng = g + 1
                    nf = ng + heuristic((nx, ny), goal)
                    heapq.heappush(pq, (nf, ng, (nx, ny), path + [action]))
        return None

    # Instance methods for game version (gold collection and hazards)
    def __init__(self, gameWorld):
        self.gameWorld = gameWorld
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

    def getActions(self, location):
        """Get valid actions from a location, avoiding hazards."""
        actions = []
        if (location.y < self.gameWorld.maxY and
            not self.gameWorld.isDangerous(location.x, location.y + 1)):
            actions.append(Directions.NORTH)
        if location.y > 0 and not self.gameWorld.isDangerous(location.x, location.y - 1):
            actions.append(Directions.SOUTH)
        if (location.x < self.gameWorld.maxX and
            not self.gameWorld.isDangerous(location.x + 1, location.y)):
            actions.append(Directions.EAST)
        if location.x > 0 and not self.gameWorld.isDangerous(location.x - 1, location.y):
            actions.append(Directions.WEST)
        return actions

    def createChildNode(self, parent, action):
        """Create a child node based on an action."""
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

    def recoverPlan(self, node):
        """Recover the path from a goal node."""
        plan = []
        current = node
        while current.parent:
            plan.append(current.action)
            current = current.parent
        plan.reverse()
        return plan

    def dfs_game(self, start, allGold):
        """DFS for game: Find path to collect all gold."""
        node = Node(start, gold_collected=set())
        stack = [node]
        explored = set()
        while stack:
            node = stack.pop()
            current_pos = (node.location.x, node.location.y)
            if current_pos in explored:
                continue
            explored.add(current_pos)
            if current_pos in allGold and current_pos not in node.gold_collected:
                node.gold_collected.add(current_pos)
                print(f"Gold found at {current_pos}")
            if node.gold_collected == allGold:
                return self.recoverPlan(node)
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
                if (child.location.x, child.location.y) not in explored:
                    stack.append(child)
        print("Failed to find all gold")
        return []

    def bfs_game(self, start, allGold):
        """BFS for game: Find shortest path to collect all gold."""
        start_node = Node(start, gold_collected=set())
        queue = [start_node]
        visited = {}  # (position, frozenset(gold_collected))
        while queue:
            node = queue.pop(0)
            current_pos = (node.location.x, node.location.y)
            new_collected = node.gold_collected.copy()
            if current_pos in allGold and current_pos not in new_collected:
                new_collected.add(current_pos)
                print(f"Collected gold at {current_pos}")
            if new_collected == allGold:
                node.gold_collected = new_collected
                return self.recoverPlan(node)
            state_key = (current_pos, frozenset(new_collected))
            if state_key in visited:
                continue
            visited[state_key] = True
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
                child.gold_collected = new_collected.copy()
                child_state = ((child.location.x, child.location.y), frozenset(child.gold_collected))
                if child_state not in visited:
                    queue.append(child)
        print("Failed to find all gold")
        return []

    def ucs_game(self, start, allGold):
        """UCS for game: Find optimal cost path to collect all gold."""
        start_node = Node(start, gold_collected=set())
        pq = [(0, id(start_node), start_node)]  # (cost, tiebreaker, node)
        explored = {}
        while pq:
            cost, _, node = heapq.heappop(pq)
            current_pos = (node.location.x, node.location.y)
            collected = node.gold_collected
            state_key = (current_pos, frozenset(collected))
            if state_key in explored and explored[state_key] <= cost:
                continue
            explored[state_key] = cost
            if current_pos in allGold and current_pos not in collected:
                collected = collected.copy()
                collected.add(current_pos)
                print(f"Collected gold at {current_pos}")
            if collected == allGold:
                node.gold_collected = collected
                return self.recoverPlan(node)
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
                child.gold_collected = collected.copy()
                child_cost = cost + 1
                child_state = ((child.location.x, child.location.y), frozenset(child.gold_collected))
                if child_state not in explored or explored[child_state] > child_cost:
                    heapq.heappush(pq, (child_cost, id(child), child))
        print("Failed to find all gold")
        return []

    def greedy_game(self, start, allGold):
        """Greedy Search for game: Minimize distance to remaining gold."""
        def heuristic(node):
            remaining = allGold - node.gold_collected
            if not remaining:
                return 0
            hx, hy = node.location.x, node.location.y
            return min(abs(gx - hx) + abs(gy - hy) for gx, gy in remaining)

        start_node = Node(start, gold_collected=set())
        pq = [(heuristic(start_node), id(start_node), start_node)]
        explored = {}
        while pq:
            h, _, node = heapq.heappop(pq)
            current_pos = (node.location.x, node.location.y)
            collected = node.gold_collected.copy()
            if current_pos in allGold and current_pos not in collected:
                collected.add(current_pos)
                print(f"Collected gold at {current_pos}")
            if collected == allGold:
                node.gold_collected = collected
                return self.recoverPlan(node)
            state_key = (current_pos, frozenset(collected))
            if state_key in explored and explored[state_key] <= h:
                continue
            explored[state_key] = h
            for action in self.getActions(node.location):
                child = self.createChildNode(node, action)
                child.gold_collected = collected.copy()
                child_h = heuristic(child)
                child_state = ((child.location.x, child.location.y), frozenset(child.gold_collected))
                if child_state not in explored or explored[child_state] > child_h:
                    heapq.heappush(pq, (child_h, id(child), child))
        print("Failed to find all gold")
        return []

    def find_path(self, algorithm_type, start, allGold):
        """Select and execute the specified game search algorithm."""
        if algorithm_type == 1:
            return self.dfs_game(start, allGold)
        elif algorithm_type == 2:
            return self.bfs_game(start, allGold)
        elif algorithm_type == 3:
            return self.ucs_game(start, allGold)
        elif algorithm_type == 4:
            return self.greedy_game(start, allGold)
        else:
            return self.dfs_game(start, allGold)  # Default to DFS