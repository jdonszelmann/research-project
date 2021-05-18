from python.mstar.identifier import Identifier
from python.mstar.state import State
from typing import Type, TypeVar

T = TypeVar("T", bound=State)


class StateCache:
    def __init__(self):
        self.cache = dict()
        # self.intermediate = use_intermediate_nodes

    def get(self, identifier: Identifier, constructor: Type[T] = State, insert: bool = True) -> T:
        if identifier in self.cache:
            return self.cache[identifier]
        elif insert:
            self.cache[identifier] = constructor(identifier)
            return self.cache[identifier]

    def reset(self):
        for i in self.cache.values():
            i.reset()
