from mapfmclient import Problem, Solution

import sys
import pathlib

this_dir = pathlib.Path(__file__).parent.absolute()

from python.algorithm import MapfAlgorithm


sys.path.insert(0, str(this_dir / "matching-epea-star"))
from src.solver.solver import Solver
from src.solver.algorithm_descriptor import AlgorithmDescriptor, Algorithm
sys.path.pop(0)


class EPEAStar(MapfAlgorithm):
    def solve(self, problem: Problem) -> Solution:
        algorithm = AlgorithmDescriptor(
            Algorithm.ExhaustiveMatchingSorting,
            independence_detection=True,
        )
        solver = Solver(problem, algorithm)
        return Solution.from_paths(solver.solve())

    @property
    def name(self) -> str:
        return "epeA* (Jaap)"
