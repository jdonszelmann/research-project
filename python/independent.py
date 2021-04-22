from __future__ import annotations
from typing import Tuple, List, Iterable
from python.mstar.planner.problem import Problem
from python.mstar.planner.problem import State
from python.mstar.planner.astar import AStar

from mapfmclient import MarkedLocation, Problem as cProblem, Solution


class MapfmState(State):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __hash__(self) -> int:
        return tuple.__hash__((self.x, self.y))

    def __eq__(self, other: MapfmState):
        return self.x == other.x and self.y == other.y

    def to_tuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def __repr__(self):
        return f"MapfmState( {self.x} {self.y} )"


class MapfmProblem(Problem):
    def __init__(self, start: MarkedLocation, end: MarkedLocation, grid: List[List[int]], width: int, height: int):
        self.start = start
        self.end = end
        self.grid = grid
        self.width = width
        self.height = height

    def wall_at(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 1

    def neighbours(self, parent: MapfmState) -> Iterable[Tuple[MapfmState, int]]:
        res = []

        if parent.y > 0 and not self.wall_at(parent.x, parent.y - 1):
            res.append(MapfmState(parent.x, parent.y - 1))

        if parent.y < self.height - 1 and not self.wall_at(parent.x, parent.y + 1):
            res.append(MapfmState(parent.x, parent.y + 1))

        if parent.x > 0 and not self.wall_at(parent.x - 1, parent.y):
            res.append(MapfmState(parent.x - 1, parent.y))

        if parent.x < self.width - 1 and not self.wall_at(parent.x + 1, parent.y):
            res.append(MapfmState(parent.x + 1, parent.y))

        return map(lambda i: (i, 1), res)

    def initial_state(self) -> MapfmState:
        return MapfmState(self.start.x, self.start.y)

    def final_state(self, state: MapfmState) -> bool:
        return state.x == self.end.x and state.y == self.end.y

    def heuristic(self, state: MapfmState) -> int:
        return abs(state.x - self.end.y) + abs(state.y - self.end.y)


def independent(problem: cProblem) -> Solution:
    solutions = []
    for (start, goal) in zip(problem.starts, problem.goals):
        p = MapfmProblem(start, goal, problem.grid, problem.width, problem.height)
        solutions.append(AStar().search(p))

    return Solution.from_paths([list(map(MapfmState.to_tuple, s)) for s in solutions])

