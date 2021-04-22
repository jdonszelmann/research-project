from __future__ import annotations

from itertools import product
from typing import Tuple, List, Iterable, Optional
from python.mstar.planner.problem import Problem
from python.mstar.planner.problem import State
from python.mstar.planner.astar import AStar

from mapfmclient import MarkedLocation, Problem as cProblem, Solution


class Coord:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __hash__(self) -> int:
        return tuple.__hash__((self.x, self.y))

    def __eq__(self, other: Coord):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f"Coord({self.x}, {self.y})"

    def __iter__(self):
        yield self.x
        yield self.y


class MapfmState(State):
    def __init__(self, coords: Iterable[Tuple[int, int]], accumulated_cost: Optional[List[int]] = None):
        self.coords = tuple((Coord(*i) for i in coords))
        self.accumulated_cost: Tuple[int] = tuple(0 for _ in self.coords) if accumulated_cost is None else tuple(accumulated_cost)

    def __hash__(self) -> int:
        return tuple.__hash__((self.coords, self.accumulated_cost))

    def __eq__(self, other: MapfmState):
        return self.coords == other.coords and self.accumulated_cost == other.accumulated_cost

    def __repr__(self):
        return f"MapfmState({self.coords}, {self.accumulated_cost})"


class MapfmProblem(Problem):
    def __init__(self, starts: List[MarkedLocation], ends: List[MarkedLocation], grid: List[List[int]], width: int, height: int):
        self.starts = starts
        self.ends = ends
        self.grid = grid
        self.width = width
        self.height = height

        self.startstate = MapfmState(map(lambda i: (i.x, i.y), starts))

    def wall_at(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 1

    def neighbours(self, parent: MapfmState) -> Iterable[Tuple[MapfmState, int]]:
        def options(location: Coord) -> List[Coord]:
            res = []

            if location.y > 0 and not self.wall_at(location.x, location.y - 1):
                res.append(Coord(location.x, location.y - 1))

            if location.y < self.height - 1 and not self.wall_at(location.x, location.y + 1):
                res.append(Coord(location.x, location.y + 1))

            if location.x > 0 and not self.wall_at(location.x - 1, location.y):
                res.append(Coord(location.x - 1, location.y))

            if location.x < self.width - 1 and not self.wall_at(location.x + 1, location.y):
                res.append(Coord(location.x + 1, location.y))

            res.append(location)

            return res

        optionlist = (options(i) for i in parent.coords)
        neighbours = product(*optionlist)

        def swapping(a, b):
            for a1 in range(len(a)):
                for a2 in range(min(a1, len(b))):
                    if a[a1] == b[a2] and b[a1] == a[a2]:
                        return False

            return True

        def cost(cs, par, ec, sc):
            res = 0
            acc = list(par.accumulated_cost)
            for index, i in enumerate(cs):

                no_cost = False
                if par.coords[index] == cs[index]:
                    for end in ec:
                        if end.x == i.x and end.y == i.y and end.color == sc[index].color:
                            res += 0
                            acc[index] += 1
                            no_cost = True
                            break

                if not no_cost:
                    res += 1 + par.accumulated_cost[index]
                    acc[index] = 0

            return res, acc

        ret = [
            (lambda c, accumulated_cost: (MapfmState(n, accumulated_cost), c))(*cost(n, parent, self.ends, self.starts))
            for n in neighbours
            if len(set(n)) == len(n) and swapping(n, parent.coords)
        ]

        return ret

    def initial_state(self) -> MapfmState:
        return self.startstate

    def final_state(self, state: MapfmState) -> bool:
        num_correct = 0
        seen = set()
        for index, coord in enumerate(state.coords):
            c = self.starts[index].color
            if coord in seen:
                return False

            seen.add(coord)

            for i in self.ends:
                if i.x == coord.x and i.y == coord.y and c == i.color:
                    num_correct += 1

        return num_correct == len(state.coords)

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


def standard_astar(problem: cProblem) -> Solution:
    starts = problem.starts

    p = MapfmProblem(starts, problem.goals, problem.grid, problem.width, problem.height)
    solution = AStar().search(p)

    paths = [[] for _ in solution[0].coords]
    for path in solution:
        for index, coord in enumerate(path.coords):
            paths[index].append((coord.x, coord.y))

    # print()
    # print([(i.x, i.y) for i in starts])
    # print([(i.x, i.y) for i in goals])
    # for i in paths:
    #     print(i)

    return Solution.from_paths(paths)
    # return Solution.from_paths([
    #     [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (6, 3)],
    #     [(6, 1), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (1, 2), (0, 2), (0, 3), (0, 3), (0, 3), (0, 3), (0, 3), (0, 3), (0, 3), (0, 3)]
    # ])

