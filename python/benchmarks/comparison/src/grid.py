from collections import defaultdict
from typing import List, TypeVar, Generic, Dict, Optional

from mapfmclient import Problem

from src.data.agent import Agent
from src.data.vertex import Vertex

A = TypeVar("A", bound=Agent)


class Grid(Generic[A]):
    def __init__(self, problem: Problem):
        self.width: int = problem.width
        self.height: int = problem.height

        self._vertices: Dict[int, Dict[int, Optional[Vertex]]] = defaultdict(
            lambda: defaultdict(lambda: None))
        for x in range(self.width):
            for y in range(self.height):
                if problem.grid[y][x] == 0:
                    self._vertices[y][x] = Vertex(x, y)

        self.agents: List[A] = self.create_agents(problem)

    def get_vertex(self, x: int, y: int) -> Optional[Vertex]:
        return self._vertices[y][x]

    def create_agents(self, problem: Problem) -> List[A]:
        raise NotImplementedError("Override this!")
