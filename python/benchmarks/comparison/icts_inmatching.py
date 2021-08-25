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


class ICTSInmatching(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        def solve_icts():
            config = SolverConfig(
                name="ICTS-m+ID+S+C",
                combs=3,
                prune=True,
                enhanced=False,
                pruned_child_gen=True,
                id=True,
                conflict_avoidance=True,
                enumerative=False,
                debug=False,
                sort_matchings=False,
            )
            return Solver(config)(problem)[0]
        return solve_with_modules(modules, solve_icts)

    @property
    def name(self) -> str:
        return "ICTS* (Thom)"
