from mapfmclient import Problem, Solution

from python.algorithm import MapfAlgorithm
from python.mstar.heuristic import Heuristics
from python.mstar.prematch.mstar import PrematchMStar


class MStar(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        solution = PrematchMStar(
            problem.grid,
            problem.starts,
            problem.goals,
            problem.width,
            problem.height,
        ).search_matchings()

        paths = [[] for _ in solution[0].identifier.actual]
        for path in solution:
            for index, coord in enumerate(path.identifier.actual):
                paths[index].append((coord.x, coord.y))

        return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "prematch M*"
