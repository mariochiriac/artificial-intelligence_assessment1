# search.py
#
# Generic search algorithms for Wumpus World (puzzle and gold modes).
#
# Written for modularity and reuse.
# Last Modified: March 18, 2025

from utils import Directions, Pose
from node import Node
from heapq import heappush, heappop

class Search:
    @staticmethod
    def get_actions(state, max_x, max_y):
        """Return valid actions from a position."""
        actions = []
        if state.y < max_y:
            actions.append(Directions.NORTH)
        if state.y > 0:
            actions.append(Directions.SOUTH)
        if state.x < max_x:
            actions.append(Directions.EAST)
        if state.x > 0:
            actions.append(Directions.WEST)
        return actions

    @staticmethod
    def apply_action(state, action):
        """Apply an action to a state, returning a new Pose."""
        new_state = Pose()
        new_state.x = state.x
        new_state.y = state.y
        if action == Directions.NORTH:
            new_state.y += 1
        elif action == Directions.SOUTH:
            new_state.y -= 1
        elif action == Directions.EAST:
            new_state.x += 1
        elif action == Directions.WEST:
            new_state.x -= 1
        return new_state

    @staticmethod
    def heuristic(state, goal):
        """Manhattan distance heuristic for A*."""
        return abs(state.x - goal.x) + abs(state.y - goal.y)

    @staticmethod
    def dfs(start, goal, max_x, max_y, format_move):
        """DFS to find a path from start to goal."""
        start_node = Node(start)
        stack = [start_node]
        explored = set()

        while stack:
            node = stack.pop()
            if (node.location.x, node.location.y) in explored:
                continue

            explored.add((node.location.x, node.location.y))

            if node.location.x == goal.x and node.location.y == goal.y:
                plan = []
                while node.parent is not None:
                    plan.append(format_move(node.action))
                    node = node.parent
                plan.reverse()
                return plan

            for action in Search.get_actions(node.location, max_x, max_y):
                child_loc = Search.apply_action(node.location, action)
                child = Node(child_loc, node, action, node.cost + 1)
                if (child.location.x, child.location.y) not in explored:
                    stack.append(child)
        return []  # No solution found

    @staticmethod
    def astar(start, goal, max_x, max_y, format_move):
        """A* to find an optimal path from start to goal."""
        start_node = Node(start)
        counter = 0  # A counter to break ties in the priority queue
        # Store (f_cost, counter, node) so heapq never compares Nodes directly
        frontier = [(0, counter, start_node)]  
        explored = set()
        came_from = {}
        g_cost = {start_node: 0}
        f_cost = {start_node: Search.heuristic(start, goal)}

        while frontier:
            # Pop the node with the lowest f cost (counter breaks ties if f is equal)
            f, _, node = heappop(frontier)  # Ignore the counter when we pop
            if (node.location.x, node.location.y) in explored:
                continue

            explored.add((node.location.x, node.location.y))

            # If we’re at the goal, build and return the plan
            if node.location.x == goal.x and node.location.y == goal.y:
                plan = []
                while node in came_from:
                    action = came_from[node][1]
                    plan.append(format_move(action))
                    node = came_from[node][0]
                plan.reverse()
                return plan

            # Check all possible moves from here
            for action in Search.get_actions(node.location, max_x, max_y):
                child_loc = Search.apply_action(node.location, action)
                child = Node(child_loc, node, action, node.cost + 1)
                tentative_g = g_cost[node] + 1  # Cost to reach this child

                if (child.location.x, child.location.y) not in explored:
                    if child not in g_cost or tentative_g < g_cost[child]:
                        g_cost[child] = tentative_g
                        f = tentative_g + Search.heuristic(child.location, goal)
                        counter += 1  # Increment counter for uniqueness
                        # Push (f, counter, child) so ties in f use counter
                        heappush(frontier, (f, counter, child))
                        came_from[child] = (node, action)
        return []  # No solution found