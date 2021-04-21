from __future__ import annotations
from heapq import heappush, heappop
from typing import Optional, List

from python.mstar.planner import Planner
from python.mstar.planner.problem import Problem, State


class AStarNode:
    def __init__(self, state: State, cost: int,  parent: Optional[AStarNode] = None):
        self.state = state
        self.parent = parent
        self.cost = cost
        if parent is not None:
            cost += parent.cost

    def backtrack(self, res: Optional[List[State]] = None) -> List[State]:
        if res is None:
            res: List[State] = []
        if self.parent is not None:
            self.parent.backtrack(res)

        res.append(self.state)

        return res

    def __repr__(self):
        return f"AStarNode({self.cost}, {self.state})"


class AStar(Planner):
    def __init__(self):
        super().__init__()

    def search(self, problem: Problem) -> List[State]:
        initial_state = problem.initial_state()
        initial_heuristic = problem.heuristic(initial_state)
        initial_node = AStarNode(initial_state, 0)

        seen = set()
        pq = []

        priority = initial_node.cost + initial_heuristic
        heappush(pq, (priority, initial_node))

        while True:
            h, curr = heappop(pq)

            if curr.state in seen:
                continue

            seen.add(curr.state)

            if problem.final_state(curr.state):
                return curr.backtrack()

            neighbours = problem.neighbours(curr.state)

            for (n, cost) in neighbours:
                if n not in seen:
                    priority = curr.cost + cost + problem.heuristic(n)
                    heappush(pq, (priority, AStarNode(n, cost, curr)))
