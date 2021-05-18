from __future__ import annotations

from itertools import product
from typing import Tuple, List, Iterable, Optional

from mapfmclient import MarkedLocation, Problem as cProblem, Solution

from python.astar.problem import AStarProblem
from python.coord import Coord
from python.algorithm import MapfAlgorithm
from python.astar.astar import AStar
from python.planner import State


class MapfmState(State):
    def __init__(self, coords: Iterable[Tuple[int, int]], accumulated_cost: Optional[List[int]] = None):
        self.coords = tuple((Coord(*i) for i in coords))
        self.accumulated_cost: Tuple[int] = tuple(0 for _ in self.coords) if accumulated_cost is None else tuple(
            accumulated_cost)

    def __hash__(self) -> int:
        return tuple.__hash__((self.coords, self.accumulated_cost))

    def __eq__(self, other: MapfmState):
        return self.coords == other.coords and self.accumulated_cost == other.accumulated_cost

    def __repr__(self):
        return f"MapfmState({self.coords}, {self.accumulated_cost})"

    def colors(self, starts: List[MarkedLocation]) -> List[int]:
        return [starts[i].color for i in range(len(self.coords))]


class MapfmProblem(AStarProblem):
    def __init__(self, starts: List[MarkedLocation], ends: List[MarkedLocation], grid: List[List[int]], width: int,
                 height: int):
        self.starts = starts
        self.ends = ends
        self.grid = grid
        self.width = width
        self.height = height

        self.start_state = MapfmState(map(lambda i: (i.x, i.y), starts))

    def wall_at(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 1

    def on_final(self, coord: Coord, color: int) -> bool:
        for i in self.ends:
            if i.x == coord.x and i.y == coord.y and i.color == color:
                return True

        return False

    @staticmethod
    def has_double(coords: Iterable[Coord]) -> bool:
        return len(set(coords)) != len(list(coords))

    def conflict(self, src, dst) -> bool:
        if self.has_double(dst):
            return True

        for a1 in range(len(src)):
            for a2 in range(min(a1, len(dst))):
                if src[a1] == dst[a2] and dst[a1] == src[a2]:
                    return True

        return False

    def neighbours(self, parent: MapfmState) -> Iterable[Tuple[MapfmState, int]]:
        # all the directions you can move in
        directions = [Coord(0, -1), Coord(0, 1), Coord(1, 0), Coord(-1, 0)]

        all_agent_possibilities = []
        for agent_position, acc, color in zip(parent.coords, parent.accumulated_cost, parent.colors(self.starts)):
            neighbours = []
            for i in directions:
                p = i + agent_position

                if not p.out_of_bounds(self.width, self.height) and not self.wall_at(p.x, p.y):
                    neighbours.append((p, 0, acc + 1))

            if self.on_final(agent_position, color):
                neighbours.append((agent_position, acc + 1, 0))
            else:
                neighbours.append((agent_position, 0, 1))

            all_agent_possibilities.append(neighbours)

        possible_next_states = product(*all_agent_possibilities)

        next_states = []
        for possible_next_state in possible_next_states:
            if self.conflict(parent.coords, [i[0] for i in possible_next_state]):
                continue

            coords = [i[0] for i in possible_next_state]
            accumulators = [i[1] for i in possible_next_state]
            cost = sum(i[2] for i in possible_next_state)

            next_state = MapfmState(coords, accumulators)
            next_states.append((next_state, cost))

        return next_states

    def initial_state(self) -> MapfmState:
        return self.start_state

    def final_state(self, state: MapfmState) -> bool:
        if self.has_double(state.coords):
            return False

        for index, (coord, color) in enumerate(zip(state.coords, state.colors(self.starts))):
            if not self.on_final(coord, color):
                return False

        return True

    def heuristic(self, state: MapfmState) -> int:
        res = 0
        for index, coord in enumerate(state.coords):
            c = self.starts[index].color
            best = None
            for i in self.ends:
                if c == i.color:
                    dist = abs(i.x - coord.x) + abs(i.y - coord.y)
                    if best is None or best < dist:
                        best = dist
            res += best
        return res


class MatchingAStar(MapfAlgorithm):
    def solve(self, problem: cProblem) -> Solution:
        starts = problem.starts

        p = MapfmProblem(starts, problem.goals, problem.grid, problem.width, problem.height)
        solution = AStar().search(p)

        paths = [[] for _ in solution[0].coords]
        for path in solution:
            for index, coord in enumerate(path.coords):
                paths[index].append((coord.x, coord.y))

        return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "AStar + Matching"
