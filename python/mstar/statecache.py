from python.mstar.identifier import Identifier
from python.mstar.state import State
from math import inf


class StateCache:
    def __init__(self):
        self.cache = dict()
        # self.intermediate = use_intermediate_nodes

    def get(self, identifier: Identifier) -> State:
        if identifier in self.cache:
            return self.cache[identifier]
        else:
            self.cache[identifier] = State(identifier)
            return self.cache[identifier]

    def reset_costs(self):
        for i in self.cache.values():
            i.cost = inf
