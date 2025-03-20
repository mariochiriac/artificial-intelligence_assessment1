# search.py - Expanded node counting
from utils import Directions
from collections import deque
import heapq

class SearchProblem:
    # Abstract base class for search problems
    def getStartState(self):
        # Returns the initial state; must be implemented by subclass
        raise NotImplementedError

    def isGoalState(self, state):
        # Checks if state is a goal; must be implemented by subclass
        raise NotImplementedError

    def getSuccessors(self, state):
        # Returns list of (next_state, action, cost) tuples; must be implemented by subclass
        raise NotImplementedError

    def heuristic(self, state):
        # Estimates cost to goal for Greedy and A*; must be implemented by subclass
        raise NotImplementedError

    def getCostOfActions(self, actions):
        # Returns total cost as number of actions
        return len(actions)
    
    def __init__(self):
        self.nodes = 0

class GameSearchProblem(SearchProblem):
    # Search problem for game version: find uncollected gold
    def __init__(self, gameWorld, start, goals):
        self.gameWorld = gameWorld
        self.start = start  # Starting position as (x, y)
        self.goals = goals  # Set of gold positions as (x, y)
        self.nodes_expanded = 0

    def getStartState(self):
        # Returns starting position
        return self.start

    def isGoalState(self, state):
        # True if state is a gold position
        return state in self.goals

    def getSuccessors(self, state):
        # Generates valid next states avoiding dangers
        self.nodes_expanded += 1  # Count node expansion
        successors = []
        x, y = state
        for action, (dx, dy) in [
            (Directions.NORTH, (0, 1)),
            (Directions.SOUTH, (0, -1)),
            (Directions.EAST, (1, 0)),
            (Directions.WEST, (-1, 0))
        ]:
            nx, ny = x + dx, y + dy
            if (0 <= nx <= self.gameWorld.maxX and 
                0 <= ny <= self.gameWorld.maxY and 
                not self.gameWorld.isDangerous(nx, ny)):
                successors.append(((nx, ny), action, 1))
        return successors

    def heuristic(self, state):
        # Manhattan distance to nearest gold; 0 if no goals
        if not self.goals:
            return 0
        return min(abs(state[0] - gx) + abs(state[1] - gy) for gx, gy in self.goals)

class PuzzleSearchProblem(SearchProblem):
    # Search problem for puzzle version: move to a goal position
    def __init__(self, start, goal, maxX, maxY):
        self.start = start  # Start position as (x, y)
        self.goal = goal    # Goal position as (x, y)
        self.maxX = maxX
        self.maxY = maxY
        self.nodes_expanded = 0

    def getStartState(self):
        # Returns start position
        return self.start

    def isGoalState(self, state):
        # True if state matches goal
        return state == self.goal

    def getSuccessors(self, state):
        # Generates valid next states within bounds
        successors = []
        self.nodes_expanded += 1  # Count node expansion
        x, y = state
        for action, (dx, dy) in [
            (Directions.NORTH, (0, 1)),
            (Directions.SOUTH, (0, -1)),
            (Directions.EAST, (1, 0)),
            (Directions.WEST, (-1, 0))
        ]:
            nx, ny = x + dx, y + dy
            if 0 <= nx <= self.maxX and 0 <= ny <= self.maxY:
                successors.append(((nx, ny), action, 1))
        return successors

    def heuristic(self, state):
        # Manhattan distance to goal
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])

def dfs(problem):
    # Depth-First Search: returns path to goal, prints nodes checked
    stack = [(problem.getStartState(), [])]
    visited = set()
    nodes_checked = 0
    while stack:
        state, path = stack.pop()
        problem.nodes_expanded += 1
        nodes_checked += 1  # Count each node explored
        if problem.isGoalState(state):
            print(f"DFS nodes checked: {nodes_checked} || up-to-date nodes expanded: {problem.nodes_expanded}")
            return path
        if state not in visited:
            visited.add(state)
            for successor, action, _ in problem.getSuccessors(state):
                if successor not in visited:
                    stack.append((successor, path + [action]))
    print(f"DFS nodes checked: {nodes_checked} (no path found)")
    return None


def bfs(problem):
    # Breadth-First Search: returns path to goal, prints nodes checked
    queue = deque([(problem.getStartState(), [])])
    visited = set()
    nodes_checked = 0
    while queue:
        state, path = queue.popleft()
        nodes_checked += 1
        problem.nodes_expanded += 1
        if problem.isGoalState(state):
            print(f"BFS nodes checked: {nodes_checked} || up-to-date nodes expanded: {problem.nodes_expanded}")
            return path
        if state not in visited:
            visited.add(state)
            for successor, action, _ in problem.getSuccessors(state):
                if successor not in visited:
                    queue.append((successor, path + [action]))
    print(f"BFS nodes checked: {nodes_checked} (no path found)")
    return None

def ucs(problem):
    # Uniform Cost Search: returns path to goal, prints nodes checked
    pq = [(0, problem.getStartState(), [])]  # (cost, state, path)
    visited = {}  # state -> cost
    nodes_checked = 0
    while pq:
        cost, state, path = heapq.heappop(pq)
        nodes_checked += 1
        problem.nodes_expanded += 1
        if problem.isGoalState(state):
            print(f"UCS nodes checked: {nodes_checked} || up-to-date nodes expanded: {problem.nodes_expanded}")
            return path
        if state not in visited or visited[state] > cost:
            visited[state] = cost
            for successor, action, step_cost in problem.getSuccessors(state):
                new_cost = cost + step_cost
                heapq.heappush(pq, (new_cost, successor, path + [action]))
    print(f"UCS nodes checked: {nodes_checked} (no path found)")
    return None

def greedy(problem):
    # Greedy Best-First Search: returns path to goal, prints nodes checked
    pq = [(problem.heuristic(problem.getStartState()), problem.getStartState(), [])]
    visited = set()
    nodes_checked = 0
    while pq:
        _, state, path = heapq.heappop(pq)
        nodes_checked += 1
        problem.nodes_expanded += 1
        if problem.isGoalState(state):
            print(f"Greedy nodes checked: {nodes_checked} || up-to-date nodes expanded: {problem.nodes_expanded}")
            return path
        if state not in visited:
            visited.add(state)
            for successor, action, _ in problem.getSuccessors(state):
                if successor not in visited:
                    h = problem.heuristic(successor)
                    heapq.heappush(pq, (h, successor, path + [action]))
    print(f"Greedy nodes checked: {nodes_checked} (no path found)")
    return None

def astar(problem):
    # A* Search: returns path to goal, prints nodes checked
    h_start = problem.heuristic(problem.getStartState())
    pq = [(h_start, 0, problem.getStartState(), [])]  # (f, g, state, path)
    visited = {}  # state -> g_cost
    nodes_checked = 0
    while pq:
        f, g, state, path = heapq.heappop(pq)
        nodes_checked += 1
        problem.nodes_expanded += 1
        if problem.isGoalState(state):
            print(f"A* nodes checked: {nodes_checked} || up-to-date nodes expanded: {problem.nodes_expanded}")
            return path
        if state not in visited or visited[state] > g:
            visited[state] = g
            for successor, action, step_cost in problem.getSuccessors(state):
                new_g = g + step_cost
                new_f = new_g + problem.heuristic(successor)
                heapq.heappush(pq, (new_f, new_g, successor, path + [action]))
    print(f"A* nodes checked: {nodes_checked} (no path found)")
    return None

# Maps algorithm numbers to functions
SEARCH_ALGORITHMS = {
    1: dfs,
    2: bfs,
    3: ucs,
    4: greedy,
    5: astar
}