from __future__ import annotations

from mapfmclient import Problem as cProblem, Solution, MarkedLocation
from python.algorithm import MapfAlgorithm
from python.mstar.solver import MStarSolver
from python.priority_queue.fast_contains import FastContainsPriorityQueue


class MStar(MapfAlgorithm):
    def solve(self, problem: cProblem) -> Solution:
        starts = problem.starts

        solution = MStarSolver(
            starts,
            problem.goals,
            problem.grid,
            problem.width,
            problem.height,
            FastContainsPriorityQueue
        ).search()

        paths = [[] for _ in solution[0].agents]
        for path in solution:
            for index, agent in enumerate(path.agents):
                paths[index].append((agent.x, agent.y))

        print(paths)
        return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "M*"
