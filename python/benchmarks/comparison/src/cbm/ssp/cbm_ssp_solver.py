from src.cbm.cbm_ctnode import CBMMakespanCTNode
from src.cbm.cbm_grid import CBMGrid
from src.cbm.cbm_high_level import CBMHighLevelSolver
from src.cbm.ssp.cbm_ssp_low_level import CBMSSPLowLevelSolver
from src.solver import Solver


class CBMSSPSolver(Solver):
    Grid = CBMGrid
    LowLevelSolver = CBMSSPLowLevelSolver
    CTNode = CBMMakespanCTNode
    HighLevelSolver = CBMHighLevelSolver

    @staticmethod
    def get_name() -> str:
        return "R.CBM.SSP"
