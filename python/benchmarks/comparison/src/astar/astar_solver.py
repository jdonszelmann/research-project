from src.astar.astar_grid import AstarGrid
from src.astar.astar_low_level import AstarLowLevelSolver
from src.solver import Solver


class AstarSolver(Solver):
    Grid = AstarGrid
    LowLevelSolver = AstarLowLevelSolver

    @staticmethod
    def get_name() -> str:
        return "R.CBS.A*"
