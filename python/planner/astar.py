from __future__ import annotations
from typing import Optional, List, Type, TypeVar

from python.planner import Planner
from python.planner.no_solution import NoSolutionError
from python.planner.problem import State, AStarProblem
from python.queue import PriorityQueue, Comparable
from python.queue.simple import SimplePriorityQueue

S = TypeVar("S", bound=State)


class AStarNode(Comparable):
    def __init__(self, state: S, cost: int, heuristic: int, parent: Optional[AStarNode] = None):
        self.state = state
        self.parent = parent
        self.cost = cost
        self.heuristic = heuristic
        if parent is not None:
            self.cost += parent.cost

    def backtrack(self, res: Optional[List[S]] = None) -> List[S]:
        if res is None:
            res: List[S] = []
        if self.parent is not None:
            self.parent.backtrack(res)

        res.append(self.state)

        return res

    @property
    def identifier(self) -> int:
        return self.identifier

    def __lt__(self, other: AStarNode):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

    def __repr__(self):
        return f"AStarNode({self.cost}, {self.state})"


class AStar(Planner):
    def __init__(self, queue_type: Type[PriorityQueue] = SimplePriorityQueue):
        super().__init__()
        self.pq_type = queue_type

    def search(self, problem: AStarProblem) -> List[S]:
        initial_state = problem.initial_state()
        initial_heuristic = problem.heuristic(initial_state)
        initial_node = AStarNode(initial_state, 0, initial_heuristic)

        seen = set()
        pq = self.pq_type()

        pq.enqueue(initial_node)

        while not pq.empty():
            curr = pq.dequeue()

            if curr.state in seen:
                continue

            seen.add(curr.state)

            if problem.final_state(curr.state):
                print(curr.cost)
                return curr.backtrack()

            neighbours = problem.neighbours(curr.state)

            for (n, cost) in neighbours:
                if n not in seen:
                    nn = AStarNode(n, cost, problem.heuristic(n), curr)
                    pq.enqueue(nn)

        raise NoSolutionError
