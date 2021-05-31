from __future__ import annotations

from typing import Iterable, Tuple

from mapfmclient import MarkedLocation

from python.mstar.rewrite.agent import Agent


class Identifier:
    def __init__(self, partial: Tuple[Agent, ...], actual: Tuple[Agent, ...]):
        self.partial = tuple(partial)
        self.actual = tuple(actual)

    @classmethod
    def from_marked_locations(cls, starts: Iterable[MarkedLocation]) -> Identifier:
        agents = tuple(
            Agent.from_marked_location(start, 0, index)
            for index, start in enumerate(starts)
        )
        return cls(agents, agents)

    def __eq__(self, other: Identifier):
        return self.partial == other.partial and self.actual == other.actual

    def __hash__(self):
        return hash((self.partial, self.actual))

    def __repr__(self):
        if self.actual == self.partial:
            return f"actual: {self.actual}"
        else:
            return f"partial: {self.partial}, actual: {self.actual}"
