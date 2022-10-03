from src.cbm.cbm_ctnode import CBMMakespanCTNode
from src.cbm.cbm_grid import CBMGrid
from src.cbm.cbm_high_level import CBMHighLevelSolver
from src.cbm.ilp.cbm_ilp_low_level import CBMILPLowLevelSolver
from src.solver import Solver


class CBMILPSolver(Solver):
    Grid = CBMGrid
    LowLevelSolver = CBMILPLowLevelSolver
    CTNode = CBMMakespanCTNode
    HighLevelSolver = CBMHighLevelSolver

    @staticmethod
    def get_name() -> str:
        return "R.CBM.ILP"
