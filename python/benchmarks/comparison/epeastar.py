from mapfmclient import Problem, Solution

import sys
import pathlib

from python.benchmarks.comparison.util import get_src_modules, solve_with_modules

this_dir = pathlib.Path(__file__).parent.absolute()

from python.algorithm import MapfAlgorithm

sys.path.insert(0, str(this_dir / "matching-epea-star"))
from src.solver.solver import Solver
from src.solver.algorithm_descriptor import AlgorithmDescriptor, Algorithm
sys.path.pop(0)


modules = get_src_modules()


class EPEAStar(MapfAlgorithm):
    def __init__(self, inmatch=False):
        self.inmatch = inmatch

    def solve(self, problem: Problem) -> Solution:
        def solve_epea():
            algorithm = AlgorithmDescriptor(
                Algorithm.HeuristicMatching if self.inmatch else Algorithm.ExhaustiveMatchingSorting,
                independence_detection=True,
            )
            solver = Solver(problem, algorithm)
            return solver.solve()

        solve = solve_with_modules(modules, solve_epea)
        return Solution.from_paths(solve)

    @property
    def name(self) -> str:
        return "epeA* (Jaap)"
