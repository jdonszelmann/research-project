from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Optional, Iterator

import itertools

from python.mstar.rewrite.agent import Agent


class CollisionSet(metaclass=ABCMeta):
    @abstractmethod
    def subset(self, other: CollisionSet) -> bool:
        """
        True if this set is a subset of another set
        """
        ...

    @abstractmethod
    def merge(self, other: CollisionSet) -> CollisionSet: ...

    @abstractmethod
    def is_colliding(self, agent: Agent) -> bool: ...

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def contains_agent(self, agent: Agent) -> bool:...

    @classmethod
    @abstractmethod
    def from_colliding_indices(cls, indices: list[tuple[int, int]]): ...


class NormalCollisionSet(CollisionSet):
    def __init__(self, inp: Optional[frozenset[int]] = None):
        if inp is None:
            inp = frozenset()

        self.set: frozenset[int] = inp

    @classmethod
    def from_colliding_indices(cls, indices: list[tuple[int, int]]):
        return cls(frozenset(itertools.chain(*indices)))

    def subset(self, other: NormalCollisionSet) -> bool:
        """
        True if this set is a subset of another set
        """

        return self.set.issubset(other.set)

    def merge(self, other: NormalCollisionSet) -> NormalCollisionSet:
        return self.__class__(other.set.union(self.set))

    def is_colliding(self, agent: Agent) -> bool:
        return agent.index in self.set

    def __len__(self) -> int:
        return len(self.set)

    def __repr__(self):
        return f"CollisionSet({self.set})"

    def contains_agent(self, agent: Agent) -> bool:
        return agent.index in self.set


class RecursiveCollisionSet(CollisionSet):
    def __init__(self, inp: Optional[frozenset[frozenset[int]]] = None):
        if inp is None:
            inp = frozenset()

        self.set: frozenset[frozenset[int]] = inp

    def __repr__(self):
        return "RecursiveCollisionSet({" + ", ".join(
            "{" + ", ".join(repr(j) for j in i) + "}" for i in self.set
        ) + "})"

    def __eq__(self, other):
        return self.set == other.set

    @classmethod
    def from_colliding_indices(cls, indices: list[tuple[int, int]]):
        sets: list[frozenset] = []
        for i in indices:
            for index, s in enumerate(sets):
                if i[0] in s or i[1] in s:
                    sets[index] = s.union(frozenset(i))
                    break
            else:
                sets.append(frozenset(i))

        return cls(frozenset(sets))

    def contains_agent(self, agent: Agent) -> bool:
        return any(agent.index in s for s in self.set)

    def subset(self, other: RecursiveCollisionSet) -> bool:
        """
        True if this set is a subset of another set
        """

        for s in self.set:
            for os in other.set:
                if s.issubset(os):
                    break
            else:
                return False
        return True

    def merge(self, other: RecursiveCollisionSet) -> RecursiveCollisionSet:
        sets: list[frozenset] = list(self.set)

        # merge
        for i in other.set:
            for index, s in enumerate(sets):
                if any(item in s for item in i):
                    sets[index] = s.union(frozenset(i))
                    break
            else:
                sets.append(frozenset(i))

        # filter overlapping
        merged_set = frozenset(
            i
            for i in sets
            if not any(i.issubset(j) for j in sets if j is not i)
        )
        return self.__class__(merged_set)

    def is_colliding(self, agent: Agent) -> bool:
        return any(agent.index in s for s in self.set)

    def __len__(self) -> int:
        return sum(len(s) for s in self.set)

    def num_groups(self) -> int:
        return len(self.set)

    def groups(self) -> Iterator[frozenset[int]]:
        yield from self.set

