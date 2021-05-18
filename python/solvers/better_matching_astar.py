from __future__ import annotations

import copy
from itertools import product
from typing import Iterable, Tuple, List

from mapfmclient import MarkedLocation, Solution, Problem as cProblem

from python.agent import Agent
from python.algorithm import MapfAlgorithm
from python.astar.astar import AStar
from python.coord import Coord
from python.astar.problem import AStarProblem
from python.planner import State


class BetterMatchingAStarState(State):
    def __init__(self, agents: List[Agent]):
        self.agents = agents

    @classmethod
    def from_starts(cls, starts: Iterable[MarkedLocation]) -> BetterMatchingAStarState:
        return cls([Agent.from_marked_location(start, 0) for start in starts])

    def child(self) -> BetterMatchingAStarState:
        return copy.deepcopy(self)

    def __hash__(self) -> int:
        return tuple.__hash__(tuple(self.agents))

    def __eq__(self, other: BetterMatchingAStarState):
        return self.agents == other.agents

    def __repr__(self):
        return f"MStarState({self.agents})"

    def __iter__(self) -> Iterable[Agent]:
        yield from self.agents


class BetterMatchingAStarProblem(AStarProblem):
    def __init__(self, starts: List[MarkedLocation], ends: List[MarkedLocation], grid: List[List[int]], width: int,
                 height: int):
        self.starts = starts
        self.ends = ends
        self.grid = grid
        self.width = width
        self.height = height

        self.start_state = BetterMatchingAStarState.from_starts(starts)

    def wall_at(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 1

    def on_final(self, agent: Agent) -> bool:
        for i in self.ends:
            if i.x == agent.x and i.y == agent.y and i.color == agent.color:
                return True

        return False

    @staticmethod
    def has_double(coords: List[Coord]) -> bool:
        """
        Finds if coords contains two the same coordinates
        """
        return len(set(coords)) != len(list(coords))

    def conflict(self, src: List[Coord], dst: List[Coord]) -> bool:
        if self.has_double(dst):
            return True

        for a1 in range(len(src)):
            for a2 in range(min(a1, len(dst))):
                if src[a1] == dst[a2] and dst[a1] == src[a2]:
                    return True

        return False

    def neighbours(self, parent: BetterMatchingAStarState) -> Iterable[Tuple[BetterMatchingAStarState, int]]:
        # all the directions you can move in
        directions = [Coord(0, -1), Coord(0, 1), Coord(1, 0), Coord(-1, 0)]

        all_agent_possibilities = []
        for agent in parent:
            neighbours = []
            for i in directions:
                p = i + agent.location

                if not p.out_of_bounds(self.width, self.height) and not self.wall_at(p.x, p.y):
                    neighbours.append((p, 0, agent.accumulated_cost + 1))

            if self.on_final(agent):
                neighbours.append((agent.location, agent.accumulated_cost + 1, 0))
            else:
                neighbours.append((agent.location, 0, 1))

            all_agent_possibilities.append(neighbours)

        possible_next_states = product(*all_agent_possibilities)

        next_states = []
        for state in possible_next_states:
            if self.conflict([i.location for i in parent.agents], [i[0] for i in state]):
                continue

            cost = 0
            next_state = parent.child()
            for agent, (coord, acc, c) in zip(next_state.agents, state):
                agent.location = coord
                agent.accumulated_cost = acc
                cost += c

            next_states.append((next_state, cost))

        return next_states

    def initial_state(self) -> BetterMatchingAStarState:
        return self.start_state

    def final_state(self, state: BetterMatchingAStarState) -> bool:
        # implied by constraints on move
        # if self.has_double(state.agents):
        #     return False

        for agent in state.agents:
            if not self.on_final(agent):
                return False

        return True

    def heuristic(self, state: BetterMatchingAStarState) -> int:
        res = 0
        for index, agent in enumerate(state.agents):
            best = None
            for i in self.ends:
                if agent.color == i.color:
                    dist = abs(i.x - agent.x) + abs(i.y - agent.y)
                    if best is None or best < dist:
                        best = dist
            res += best
        return res


class BetterMatchingAStar(MapfAlgorithm):
    def solve(self, problem: cProblem) -> Solution:
        starts = problem.starts

        p = BetterMatchingAStarProblem(starts, problem.goals, problem.grid, problem.width, problem.height)
        solution = AStar().search(p)

        paths = [[] for _ in solution[0].agents]
        for path in solution:
            for index, coord in enumerate(path.agents):
                paths[index].append((coord.x, coord.y))

        return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "AStar"
