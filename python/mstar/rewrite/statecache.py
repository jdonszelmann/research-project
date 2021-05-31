from python.mstar.rewrite.identifier import Identifier
from python.mstar.rewrite.state import State
from python.mstar.rewrite.config import Config
from typing import Type, TypeVar

T = TypeVar("T", bound=State)


class StateCache:
    def __init__(self, cfg: Config, constructor: Type[T]):
        self.cache = dict()
        self.constructor = constructor
        self.cfg = cfg

    def get(self,
            identifier: Identifier,
            insert: bool = True
            ) -> T:
        if identifier in self.cache:
            return self.cache[identifier]
        elif insert:
            self.cache[identifier] = self.constructor(self.cfg, identifier)
            return self.cache[identifier]

    def reset(self):
        for i in self.cache.values():
            i.reset()
