from __future__ import annotations

from typing import Tuple

from src.data.agent import Agent
from src.data.vertex import Vertex


class Constraint:
    def __init__(self, a_i: Agent, t: int) -> None:
        self.a_i = a_i
        self.t = t

    def __str__(self) -> str:
        return f"[{self.a_i}, t{self.t}]"

    def __hash__(self) -> int:
        return hash((self.a_i, self.t))

    def __eq__(self, other: Constraint) -> bool:
        return self.a_i.id == other.a_i.id and self.t == other.t


class VertexConstraint(Constraint):
    def __init__(self, v: Vertex, a_i: Agent, t: int) -> None:
        super().__init__(a_i, t)
        self.v = v

    def __str__(self) -> str:
        return f"{self.v} {super().__str__()}"

    def __hash__(self) -> int:
        return hash((self.v, super().__hash__()))

    def __eq__(self, other: VertexConstraint) -> bool:
        return self.v == other.v and super().__eq__(other)


class EdgeConstraint(Constraint):
    def __init__(self, e: Tuple[Vertex, Vertex], a_i: Agent, t: int) -> None:
        super().__init__(a_i, t)
        self.e = e

    def __str__(self) -> str:
        return f"({self.e[0]}, {self.e[1]}) {super().__str__()}"

    def __hash__(self) -> int:
        return hash((self.e, super().__hash__()))

    def __eq__(self, other: EdgeConstraint) -> bool:
        return self.e == other.e and super().__eq__(other)
