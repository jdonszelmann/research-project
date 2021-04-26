from __future__ import annotations
from typing import Optional, List, Type, TypeVar

from python.planner import Planner
from python.planner.no_solution import NoSolutionError
from python.planner.problem import State, MStarProblem
from python.queue import PriorityQueue, Comparable, UniqueIdentifier

S = TypeVar("S", bound=State)


class MStarState(Comparable, UniqueIdentifier):
    def __init__(self, state: S, cost: int, heuristic: int, parent: Optional[MStarState] = None):
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
        return self.state.identifier

    def __lt__(self, other: MStarState):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

    def __repr__(self):
        return f"MStarNode({self.cost}, {self.state})"


class MStar(Planner):
    def __init__(self, queue_type: Type[PriorityQueue]):
        super().__init__()
        self.pq_type = queue_type

    def search(self, problem: MStarProblem) -> List[S]:
        initial_state = problem.initial_state()
        initial_heuristic = problem.heuristic(initial_state)
        initial_node = MStarState(initial_state, 0, initial_heuristic)

        pq = self.pq_type()

        pq.enqueue(initial_node)

        while not pq.empty():
            curr = pq.dequeue()

            if problem.final_state(curr.state):
                print(curr.cost)
                return curr.backtrack()

            neighbours = problem.neighbours(curr.state, pq.__contains__)

            for (n, cost) in neighbours:
                n.next(curr.state)
                nn = MStarState(n, cost, problem.heuristic(n), curr)
                pq.enqueue(nn)

        raise NoSolutionError
