from src.low_level import LowLevelSolver
from src.high_level import HighLevelSolver
from src.grid import Grid
from src.ctnode import CTNode


class Solver:
    Grid = Grid
    LowLevelSolver = LowLevelSolver
    HighLevelSolver = HighLevelSolver
    CTNode = CTNode

    @staticmethod
    def get_name() -> str:
        raise NotImplementedError("Extend this one")
