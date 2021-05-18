from mapfmclient import Problem, Solution

from python.algorithm import MapfAlgorithm
from python.mstar.prematch.normal import MatchingMStar


class MStar(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        solution = MatchingMStar(
            problem.grid,
            problem.starts,
            problem.goals,
            problem.width,
            problem.height,
        ).search_matchings(od=False)

        paths = [[] for _ in solution[0].identifier.actual]
        for path in solution:
            for index, coord in enumerate(path.identifier.actual):
                paths[index].append((coord.x, coord.y))

        return Solution.from_paths(paths)

        # solution = Heuristics(
        #     problem.grid,
        #     problem.starts,
        #     problem.goals,
        #     problem.width,
        #     problem.height,
        # ).m_star()
        #
        # paths = [[] for _ in solution[0].identifier.actual]
        # for path in solution:
        #     for index, coord in enumerate(path.identifier.actual):
        #         paths[index].append((coord.x, coord.y))
        #
        # return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "M*"