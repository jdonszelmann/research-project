from mapfmclient import Problem, Solution

from python.algorithm import MapfAlgorithm
from python.mstar.heuristic import Heuristics
from python.mstar.prematch.mstar import PrematchMStar
from python.mstar.visualizer import Visualizer


class MStar(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:

        visualizer = Visualizer(
            problem.grid,
            problem.starts,
            problem.goals,
            problem.width,
            problem.height
        )

        h = PrematchMStar(
            problem.grid,
            problem.starts,
            problem.goals,
            problem.width,
            problem.height,
        )
        visualizer.run(h.search_matchings, True, visualizer)

        # never actually return attempts made with visual mode
        exit(0)
        return Solution.from_paths([])


    @property
    def name(self) -> str:
        return "visual prematch M*"
