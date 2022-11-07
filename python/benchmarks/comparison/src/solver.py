from python.benchmarks.comparison.src.low_level import LowLevelSolver
from python.benchmarks.comparison.src.high_level import HighLevelSolver
from python.benchmarks.comparison.src.grid import Grid
from python.benchmarks.comparison.src.ctnode import CTNode


class Solver:
    Grid = Grid
    LowLevelSolver = LowLevelSolver
    HighLevelSolver = HighLevelSolver
    CTNode = CTNode

    @staticmethod
    def get_name() -> str:
        raise NotImplementedError("Extend this one")
