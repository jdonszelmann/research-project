from mapfmclient import Problem, Solution

from python.algorithm import MapfAlgorithm
from python.mstar.heuristic import Heuristics
from python.mstar.prematch.normal import MatchingMStar


class MStarOD(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        try:
            solution = MatchingMStar(
                problem.grid,
                problem.starts,
                problem.goals,
                problem.width,
                problem.height,
            ).search_matchings(od=True)

            paths = [[] for _ in solution[0].identifier.actual]
            for path in solution:
                for index, coord in enumerate(path.identifier.actual):
                    paths[index].append((coord.x, coord.y))

            return Solution.from_paths(paths)
        except Exception:
            print(problem.grid)
            print(problem.starts)
            print(problem.goals)
            raise

        # solution = Heuristics(
        #     problem.grid,
        #     problem.starts,
        #     problem.goals,
        #     problem.width,
        #     problem.height,
        # ).m_star_od()
        #
        # paths = [[] for _ in solution[0].identifier.actual]
        # for path in solution:
        #     for index, coord in enumerate(path.identifier.actual):
        #         paths[index].append((coord.x, coord.y))
        #
        # return Solution.from_paths(paths)

    @property
    def name(self) -> str:
        return "M* + OD"
