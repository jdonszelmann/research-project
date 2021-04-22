from __future__ import annotations
from heapq import heappush, heappop
from typing import Optional, List

from python.mstar.planner import Planner
from python.mstar.planner.problem import Problem, State


class AStarNode:
    def __init__(self, state: State, cost: int, heuristic: int, parent: Optional[AStarNode] = None):
        self.state = state
        self.parent = parent
        self.cost = cost
        self.heuristic = heuristic
        if parent is not None:
            self.cost += parent.cost

    def backtrack(self, res: Optional[List[State]] = None) -> List[State]:
        if res is None:
            res: List[State] = []
        if self.parent is not None:
            self.parent.backtrack(res)

        res.append(self.state)

        return res

    def __lt__(self, other: AStarNode):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

    def __repr__(self):
        return f"AStarNode({self.cost}, {self.state})"


class AStar(Planner):
    def __init__(self):
        super().__init__()

    def search(self, problem: Problem) -> List[State]:
        initial_state = problem.initial_state()
        initial_heuristic = problem.heuristic(initial_state)
        initial_node = AStarNode(initial_state, 0, initial_heuristic)

        seen = set()
        pq = []

        heappush(pq, initial_node)

        while True:
            curr: AStarNode = heappop(pq)

            if curr.state in seen:
                continue

            seen.add(curr.state)

            if problem.final_state(curr.state):
                print(curr.cost)
                return curr.backtrack()


            neighbours = problem.neighbours(curr.state)

            for (n, cost) in neighbours:
                if n not in seen:
                    n.next(curr.state)
                    nn = AStarNode(n, cost, problem.heuristic(n), curr)
                    heappush(pq, nn)
