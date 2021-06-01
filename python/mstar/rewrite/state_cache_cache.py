from __future__ import annotations

from python.mstar.rewrite.statecache import StateCache
from python.mstar.rewrite.state import State


# TODO: copy or not?
class StateCacheCache:
    """
    Remembers state caches, so when the same agents come in collision
    again their statecaches are remembered
    """

    def __init__(self, state: State, cache: StateCache):
        self.cache: dict[
            frozenset[int, ...],  # indices
            StateCache
        ] = {}

        agents = state.identifier.actual
        self.cache[frozenset(agent.index for agent in agents)] = cache

    def add(self, item: frozenset[int], cache: StateCache):
        self.cache[item] = cache

    def __contains__(self, item: frozenset[int]) -> bool:
        return item in self.cache

    def get(self, item: frozenset[int]) -> StateCache:
        return self.cache[item]
