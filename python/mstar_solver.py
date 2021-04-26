from __future__ import annotations

import copy
from itertools import product
from typing import List, Iterable, Tuple, Set, Callable

from mapfmclient import Problem as cProblem, Solution, MarkedLocation
from python.algorithm import MapfAlgorithm
from python.better_matching_astar import Agent
from python.coord import Coord
from python.planner.mstar import MStar, MStarState
from python.planner.problem import MStarProblem
from python.queue.fast_contains import FastContainsPriorityQueue
from python.queue.unique_identifier import UniqueIdentifier


class MStarSolverState(MStarState):
    def __init__(self, agents: List[Agent], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agents = agents
        self.back_set: Set[MStarSolverState] = set()
        self.collision_set: Set[Agent] = set()

    @classmethod
    def from_starts(cls, starts: Iterable[MarkedLocation]) -> MStarSolverState:
        return cls([Agent.from_marked_location(start, 0) for start in starts])

    def child(self) -> MStarSolverState:
        return copy.deepcopy(self)

    def __hash__(self) -> int:
        return hash(self.identifier)

    def __eq__(self, other: MStarSolverState):
        return self.identifier == other.identifier

    def __repr__(self):
        return f"MStarState({self.agents}, {self.back_set}, {self.collision_set})"

    def __iter__(self) -> Iterable[Agent]:
        yield from self.agents


class MStarSolverProblem(MStarProblem):
    def __init__(self, starts: List[MarkedLocation], ends: List[MarkedLocation], grid: List[List[int]], width: int,
                 height: int):
        self.starts = starts
        self.ends = ends
        self.grid = grid
        self.width = width
        self.height = height

        self.start_state = MStarSolverState.from_starts(starts)

    def wall_at(self, x: int, y: int) -> bool:
        return self.grid[y][x] == 1

    def on_final(self, agent: Agent) -> bool:
        for i in self.ends:
            if i.x == agent.x and i.y == agent.y and i.color == agent.color:
                return True

        return False

    @staticmethod
    def collisions(old_state: List[Agent], new_state: List[Agent]) -> Set[Agent]:
        assert len(old_state) == len(new_state)
        res = set()

        for a1 in range(len(old_state)):
            for a2 in range(min(a1, len(new_state))):
                if new_state[a1] == new_state[a2]:
                    res.add(new_state[a1])
                    res.add(new_state[a2])

                elif old_state[a1] == new_state[a2] and new_state[a1] == old_state[a2]:
                    # TODO: is this right?
                    res.add(old_state[a1])
                    res.add(new_state[a2])

        return res

    # all the directions you can move in
    directions = [Coord(0, -1), Coord(0, 1), Coord(1, 0), Coord(-1, 0)]

    def neighbours(self,
                   parent: MStarSolverState,
                   ) -> Tuple[Iterable[Tuple[MStarSolverState, int]], Iterable[MStarSolverState]]:
        all_agent_possibilities = []
        for agent in parent:
            neighbours = []
            for i in self.directions:
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
        readded_states = []
        for state in possible_next_states:

            cost = 0
            next_state = parent.child()
            # TODO: get rid of this loop, I feel it's not necessary
            for agent, (coord, acc, c) in zip(next_state.agents, state):
                agent.location = coord
                agent.accumulated_cost = acc
                cost += c

            collisions = self.collisions(parent.agents, next_state.agents)
            next_state.back_set.add(parent)
            next_state.collision_set = next_state.collision_set.union(collisions)

            readded_states.extend(self.backprop(parent, next_state.collision_set, in_queue))

            if len(collisions) == 0:
                next_states.append((next_state, cost))

        return next_states, readded_states

    def backprop(self,
                 parent: MStarSolverState,
                 new_collision_set: Set[Agent],
                 in_queue: Callable[[UniqueIdentifier], bool]
                 ) -> Iterable[Tuple[MStarSolverState, int]]:

        res = []
        if not new_collision_set.issubset(parent.collision_set):
            parent.collision_set.union(new_collision_set)
            # TODO: is in_queue necessary?
            if not in_queue(parent):
                res.append()



    def initial_state(self) -> MStarSolverState:
        return self.start_state

    def final_state(self, state: MStarSolverState) -> bool:
        # implied by constraints on move
        # if self.has_double(state.agents):
        #     return False

        for agent in state.agents:
            if not self.on_final(agent):
                return False

        return True

    def heuristic(self, state: MStarSolverState) -> int:
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


class MStarSolver(MapfAlgorithm):
    def solve(self, problem: cProblem) -> Solution:
        starts = problem.starts

        p = MStarSolverProblem(starts, problem.goals, problem.grid, problem.width, problem.height)
        solution = MStar(FastContainsPriorityQueue).search(p)

        paths = [[] for _ in solution[0].agents]
        for path in solution:
            for index, agent in enumerate(path.agents):
                paths[index].append((agent.x, agent.y))

        return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "M*"
