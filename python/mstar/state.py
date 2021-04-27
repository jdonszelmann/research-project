from __future__ import annotations

import copy
from typing import Optional, List, Set, Iterable, Callable

from mapfmclient import MarkedLocation

from python.agent import Agent
from python.priority_queue import Comparable, UniqueIdentifier


class MStarState(Comparable, UniqueIdentifier):
    def __init__(self, agents: List[Agent], cost: int, heuristic: int, parent: Optional[MStarState] = None):
        self.parent = parent
        self.cost = cost
        self.heuristic = heuristic
        if parent is not None:
            self.cost += parent.cost

        self.agents = agents
        self.back_set: Set[MStarState] = set()
        self.collision_set: Set[Agent] = set()

    def backtrack(self, res: Optional[List[MStarState]] = None) -> List[MStarState]:
        if res is None:
            res: List[MStarState] = []
        if self.parent is not None:
            self.parent.backtrack(res)

        res.append(self)

        return res

    @property
    def priority(self) -> int:
        return self.cost + self.heuristic

    def __lt__(self, other: MStarState):
        return self.priority < other.priority

    def __repr__(self):
        return f"MStarNode({self.cost}, {self.agents}, {self.back_set}, {self.collision_set})"

    def set_heuristic(self, heuristic: Callable[[MStarState], int]):
        self.heuristic = heuristic(self)

    @classmethod
    def from_starts(cls, starts: Iterable[MarkedLocation], heuristic: Callable[[MStarState], int]) -> MStarState:
        res = cls(
            [Agent.from_marked_location(start, 0) for start in starts],
            cost=0,
            heuristic=0,
            parent=None,
        )
        res.set_heuristic(heuristic)
        return res

    def child(self) -> MStarState:
        return copy.deepcopy(self)

    def __hash__(self) -> int:
        return hash(self.identifier)

    def __eq__(self, other: MStarState):
        return self.identifier == other.identifier

    def __iter__(self) -> Iterable[Agent]:
        yield from self.agents
