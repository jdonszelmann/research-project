from mapfmclient import Problem, Solution

import sys
import pathlib

from python.benchmarks.comparison.util import get_src_modules, solve_with_modules

this_dir = pathlib.Path(__file__).parent.absolute()

from python.algorithm import MapfAlgorithm

sys.path.insert(0, str(this_dir / "icts-m"))
from src.ictsm .solver import Solver
from src.ictsm .solver_config import SolverConfig
sys.path.pop(0)


modules = get_src_modules()


class ICTS(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        def solve_icts():
            config = SolverConfig(
                name="Exh+E+B+O+ID",
                combs=3,
                prune=True,
                enhanced=True,
                pruned_child_gen=False,
                id=True,
                conflict_avoidance=True,
                enumerative=True,
                debug=False,
                sort_matchings=True,
                budget_search=True,
            )
            return Solver(config, problem)()

        solve = solve_with_modules(modules, solve_icts)
        return Solution.from_paths(solve)

    @property
    def name(self) -> str:
        return "ICTS* (Thom)"
