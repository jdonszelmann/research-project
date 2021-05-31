from python.mstar.rewrite.identifier import Identifier
from python.mstar.rewrite.state import State
from typing import Type, TypeVar

T = TypeVar("T", bound=State)


class StateCache:
    def __init__(self, constructor: Type[T]):
        self.cache = dict()
        self.constructor = constructor

    def get(self,
            identifier: Identifier,
            insert: bool = True
            ) -> T:
        if identifier in self.cache:
            return self.cache[identifier]
        elif insert:
            self.cache[identifier] = self.constructor(identifier)
            return self.cache[identifier]

    def reset(self):
        for i in self.cache.values():
            i.reset()
