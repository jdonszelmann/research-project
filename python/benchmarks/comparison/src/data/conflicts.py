from typing import Tuple

from src.data.agent import Agent
from src.data.vertex import Vertex


class Conflict:
    def __init__(self, a_i: Agent, a_j: Agent, t: int) -> None:
        self.a_i = a_i
        self.a_j = a_j
        self.t = t


class EdgeConflict(Conflict):
    def __init__(self, e: Tuple[Vertex, Vertex], a_i: Agent, a_j: Agent,
                 t: int):
        super().__init__(a_i, a_j, t)
        self.e = e


class VertexConflict(Conflict):
    def __init__(self, v: Vertex, a_i: Agent, a_j: Agent, t: int):
        super().__init__(a_i, a_j, t)
        self.v = v
