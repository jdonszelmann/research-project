from __future__ import annotations

from typing import Optional

from math import inf

from python.mstar.rewrite.identifier import Identifier
from python.mstar.rewrite.collisionset import NormalCollisionSet, CollisionSet
from python.mstar.rewrite.path import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from python.mstar.rewrite.heuristic import Heuristic


class State:
    def __init__(self, identifier: Identifier):
        self.identifier: Identifier = identifier

        self.collision_set: CollisionSet = NormalCollisionSet()
        self.back_set = {}

        self.parent = None
        self.child = None

        self.cost = inf
        self.heuristic = None

        self.hash = None

    def __hash__(self):
        if self.hash is None:
            self.hash = hash(self.identifier.partial)

        return self.hash

    def reset(self):
        self.cost = inf

    def copy(self) -> State:
        s = State(self.identifier)
        s.cost = self.cost
        s.heuristic = self.heuristic
        s.parent = self.parent
        # TODO: Copy?
        s.collision_set = self.collision_set
        s.back_set = self.back_set.copy()
        return s

    @property
    def priority(self) -> int:
        return self.cost + self.heuristic

    @property
    def is_standard(self) -> bool:
        return self.identifier.partial == self.identifier.actual

    def merge(self, other_collision_set: set[int]):
        self.collision_set = self.collision_set.union(other_collision_set)

    def is_collision_subset(self, other_set) -> bool:
        return other_set.issubset(self.collision_set)

    def add_back_set(self, state: State):
        self.back_set[state.identifier] = state

    def get_back_set(self):
        return self.back_set.values()

    def __backtrack_internal(self, res: Optional[list[State]] = None) -> list[State]:
        if res is None:
            res: list[State] = []
        if self.parent is not None:
            self.parent.__backtrack_internal(res)

        if self.is_standard:
            res.append(self)

        return res

    def backtrack(self) -> Path:
        return Path(self.__backtrack_internal(None))

    def __eq__(self, other: State) -> bool:
        return self.identifier == other.identifier

    def __gt__(self, other: State) -> bool:
        return self.priority > other.priority

    def __ge__(self, other: State) -> bool:
        return self.priority >= other.priority

    def __lt__(self, other: State) -> bool:
        return self.priority < other.priority

    def __le__(self, other: State) -> bool:
        return self.priority <= other.priority

    def set_heuristic(self, heuristic: Heuristic):
        self.heuristic = heuristic.heuristic(self)

    def merge_collision_sets(self, other: CollisionSet):
        self.collision_set = self.collision_set.merge(other)

    def __repr__(self):
        return f"cost: {self.cost}, heuristic: {self.heuristic}, identifier: {self.identifier}"
