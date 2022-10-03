from __future__ import annotations

from queue import PriorityQueue
from typing import Set, Optional, List

from src.data.vertex import Vertex
from src.grid import Grid
from src.paths import StandardAgentSolution


class AstarNode:
    def __init__(self, v: Vertex, t: int, astar: AstarBase,
                 parent: Optional[AstarNode]):
        self.v = v
        self.t = t

        self._f_score: Optional[int] = None

        self._astar = astar
        self.parent = parent

    @property
    def f_score(self) -> int:
        if self._f_score is None:
            self._f_score = self.t + self._astar.heuristic(self.v)
        return self._f_score

    def move(self, v: Vertex) -> AstarNode:
        return AstarNode(v, self.t + 1, self._astar, self)

    def __hash__(self) -> int:
        return hash(
            (self.v, self.t)) if self._astar.include_time else hash(self.v)

    def __lt__(self, other: AstarNode) -> bool:
        return self.f_score < other.f_score

    def __str__(self) -> str:
        return f"[{self.f_score}, t{self.t}] {self.v}"

    def __eq__(self, other: AstarNode) -> bool:
        return self.v == other.v and (not self._astar.include_time
                                      or self.t == other.t)


class AstarBase:
    def __init__(self, grid: Grid, start: Vertex, include_time: bool = True):
        self.grid = grid
        self.start = start
        self.include_time = include_time

    def solve(self) -> Optional[StandardAgentSolution]:
        visited_states: Set[AstarNode] = set()

        to_visit: PriorityQueue[AstarNode] = PriorityQueue()
        to_visit.put(AstarNode(self.start, 0, self, None))

        while not to_visit.empty():
            current_state = to_visit.get()
            visited_states.add(current_state)

            if self.is_goal_state(current_state):
                return self.get_path(current_state)

            neighbours = self.get_neighbours(current_state)

            for neighbour in neighbours:
                if neighbour in visited_states:
                    continue

                if neighbour not in to_visit.queue:
                    to_visit.put(neighbour)

        return None

    def heuristic(self, v: Vertex) -> int:
        raise NotImplementedError("Override this one")

    def is_goal_state(self, state: AstarNode) -> bool:
        raise NotImplementedError("Override this one")

    def get_vertex_at(self, x: int, y: int,
                      current_state: AstarNode) -> Optional[Vertex]:
        return self.grid.get_vertex(x, y)

    def get_neighbours(self, state: AstarNode) -> List[AstarNode]:
        neighbours: List[AstarNode] = []

        for dx, dy in [(0, 0), (0, 1), (1, 0), (-1, 0), (0, -1)]:
            next_vertex = self.get_vertex_at(state.v.x + dx, state.v.y + dy,
                                             state)
            if next_vertex is None:
                continue

            neighbours.append(state.move(next_vertex))

        return neighbours

    @staticmethod
    def get_path(state: AstarNode) -> StandardAgentSolution:
        path = StandardAgentSolution()

        parent = state
        while parent is not None:
            path.insert(0, parent.v)
            parent = parent.parent

        return path
