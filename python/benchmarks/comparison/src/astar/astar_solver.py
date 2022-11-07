from python.benchmarks.comparison.src.astar.astar_grid import AstarGrid
from python.benchmarks.comparison.src.astar.astar_low_level import AstarLowLevelSolver
from python.benchmarks.comparison.src.solver import Solver


class AstarSolver(Solver):
    Grid = AstarGrid
    LowLevelSolver = AstarLowLevelSolver

    @staticmethod
    def get_name() -> str:
        return "R.CBS.A*"
